from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from .models.paper import Paper

INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def clean_component(value: str, fallback: str, max_len: int = 100) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    value = INVALID.sub(" ", value)
    value = re.sub(r"\s+", " ", value).strip(" .-")
    return (value or fallback)[:max_len].rstrip(" .-")


def filename_for(paper: Paper, ext: str = "pdf", max_total: int = 220) -> str:
    year = str(paper.year or "Unknown Year")
    journal = clean_component(paper.journal_abbr or paper.journal, "Unknown Journal", 45)
    author = clean_component(paper.first_author, "Unknown", 40)
    prefix = f"{year} - {journal} - {author} - "
    available = max(24, max_total - len(prefix) - 1 - len(ext))
    title = clean_component(paper.title, "Untitled", available)
    return f"{prefix}{title}.{ext}"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    for i in range(1, 10000):
        candidate = path.with_name(f"{path.stem} ({i}){path.suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Unable to create unique filename for {path}")
