from __future__ import annotations

import csv
from pathlib import Path


def export_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def cite_key(row: dict) -> str:
    author = (row.get("authors") or "Unknown").split(";")[0].strip().split()[-1]
    return f"{author}{row.get('year') or 'nd'}".replace(" ", "")


def export_bibtex(rows: list[dict], path: Path) -> None:
    blocks: list[str] = []
    for row in rows:
        block = (
            f"@article{{{cite_key(row)},\n"
            f"  title={{{row.get('title', '')}}},\n"
            f"  author={{{(row.get('authors') or '').replace(';', ' and')}}},\n"
            f"  journal={{{row.get('journal', '')}}},\n"
            f"  year={{{row.get('year') or ''}}},\n"
            f"  doi={{{row.get('doi', '')}}}\n"
            "}"
        )
        blocks.append(block)
    path.write_text("\n\n".join(blocks), encoding="utf-8")


def export_ris(rows: list[dict], path: Path) -> None:
    output: list[str] = []
    for row in rows:
        output.extend(["TY  - JOUR", f"TI  - {row.get('title', '')}"])
        for author in (row.get("authors") or "").split(";"):
            if author.strip():
                output.append(f"AU  - {author.strip()}")
        output.extend(
            [
                f"JO  - {row.get('journal', '')}",
                f"PY  - {row.get('year') or ''}",
                f"DO  - {row.get('doi', '')}",
                "ER  - ",
                "",
            ]
        )
    path.write_text("\n".join(output), encoding="utf-8")
