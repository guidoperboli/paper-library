from __future__ import annotations

from urllib.parse import quote

from ..models.paper import Paper
from ..utils.http import HttpClient


class CrossrefConnector:
    def __init__(self, client: HttpClient, email: str | None = None):
        self.client = client
        self.email = email

    def fetch(self, doi: str) -> tuple[Paper | None, dict]:
        params = {"mailto": self.email} if self.email else {}
        data = self.client.get_json(f"https://api.crossref.org/works/{quote(doi, safe='')}", params=params)
        if not data:
            return None, {}
        msg = data.get("message", {})
        authors = []
        for a in msg.get("author", []):
            full = " ".join(x for x in [a.get("given", ""), a.get("family", "")] if x).strip()
            if full:
                authors.append(full)
        year = None
        parts = (msg.get("published-print") or msg.get("published-online") or msg.get("issued") or {}).get("date-parts", [])
        if parts and parts[0]:
            year = parts[0][0]
        paper = Paper(
            doi=doi,
            title=(msg.get("title") or [""])[0],
            authors=authors,
            journal=(msg.get("container-title") or [""])[0],
            year=year,
            publisher=msg.get("publisher", ""),
            abstract=msg.get("abstract", "") or "",
            landing_url=msg.get("URL", "") or "",
            source="crossref",
        )
        return paper, data
