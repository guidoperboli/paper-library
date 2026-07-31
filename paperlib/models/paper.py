from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Paper:
    doi: str
    title: str = ""
    authors: list[str] = field(default_factory=list)
    journal: str = ""
    journal_abbr: str = ""
    year: int | None = None
    publisher: str = ""
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    scopus_id: str = ""
    openalex_id: str = ""
    semantic_scholar_id: str = ""
    is_open_access: bool | None = None
    oa_status: str = ""
    license: str = ""
    landing_url: str = ""
    pdf_url: str = ""
    pdf_path: str = ""
    metadata_path: str = ""
    source: str = ""
    status: str = "pending"
    error: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def first_author(self) -> str:
        if not self.authors:
            return "Unknown"
        name = self.authors[0].strip()
        if "," in name:
            return name.split(",", 1)[0].strip() or "Unknown"
        return name.split()[-1] if name.split() else "Unknown"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["authors"] = "; ".join(self.authors)
        data["keywords"] = "; ".join(self.keywords)
        data.pop("raw", None)
        return data
