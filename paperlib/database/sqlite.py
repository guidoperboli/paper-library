from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from ..models.paper import Paper

SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
 doi TEXT PRIMARY KEY, title TEXT, authors TEXT, journal TEXT, journal_abbr TEXT,
 year INTEGER, publisher TEXT, abstract TEXT, keywords TEXT, scopus_id TEXT,
 openalex_id TEXT, semantic_scholar_id TEXT, is_open_access INTEGER, oa_status TEXT,
 license TEXT, landing_url TEXT, pdf_url TEXT, pdf_path TEXT, metadata_path TEXT,
 source TEXT, status TEXT, error TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
 updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year);
CREATE INDEX IF NOT EXISTS idx_papers_journal ON papers(journal);
CREATE INDEX IF NOT EXISTS idx_papers_status ON papers(status);
"""


class LibraryDB:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.executescript(SCHEMA)

    def connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def get(self, doi: str):
        with self.connect() as con:
            row = con.execute("SELECT * FROM papers WHERE doi=?", (doi,)).fetchone()
            return dict(row) if row else None

    def upsert(self, paper: Paper) -> None:
        d = paper.to_dict()
        d["is_open_access"] = None if paper.is_open_access is None else int(paper.is_open_access)
        cols = list(d)
        values = [d[c] for c in cols]
        updates = ",".join(f"{c}=excluded.{c}" for c in cols if c != "doi") + ",updated_at=CURRENT_TIMESTAMP"
        sql = f"INSERT INTO papers ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)}) ON CONFLICT(doi) DO UPDATE SET {updates}"
        with self.connect() as con:
            con.execute(sql, values)

    def search(self, query: str = "", author: str = "", journal: str = "", year: int | None = None, limit: int = 100):
        clauses, params = [], []
        if query:
            clauses.append("(title LIKE ? OR abstract LIKE ? OR keywords LIKE ?)")
            params += [f"%{query}%"] * 3
        if author:
            clauses.append("authors LIKE ?")
            params.append(f"%{author}%")
        if journal:
            clauses.append("(journal LIKE ? OR journal_abbr LIKE ?)")
            params += [f"%{journal}%"] * 2
        if year is not None:
            clauses.append("year=?")
            params.append(year)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self.connect() as con:
            rows = con.execute(f"SELECT * FROM papers{where} ORDER BY year DESC, title LIMIT ?", (*params, limit)).fetchall()
            return [dict(r) for r in rows]

    def all(self):
        with self.connect() as con:
            return [dict(r) for r in con.execute("SELECT * FROM papers ORDER BY year DESC, title").fetchall()]

    def stats(self):
        with self.connect() as con:
            return {
                "total": con.execute("SELECT COUNT(*) FROM papers").fetchone()[0],
                "downloaded": con.execute("SELECT COUNT(*) FROM papers WHERE status='downloaded'").fetchone()[0],
                "open_access": con.execute("SELECT COUNT(*) FROM papers WHERE is_open_access=1").fetchone()[0],
                "errors": con.execute("SELECT COUNT(*) FROM papers WHERE status='error'").fetchone()[0],
            }
