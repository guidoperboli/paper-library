from __future__ import annotations

from .journals import abbreviate
from .models.paper import Paper

FIELDS = ["title", "journal", "year", "publisher", "abstract", "scopus_id", "openalex_id",
          "semantic_scholar_id", "oa_status", "license", "landing_url", "pdf_url"]


def merge_papers(doi: str, papers: list[Paper]) -> Paper:
    result = Paper(doi=doi)
    for p in papers:
        for field in FIELDS:
            if not getattr(result, field) and getattr(p, field):
                setattr(result, field, getattr(p, field))
        if not result.authors and p.authors:
            result.authors = p.authors
        if not result.keywords and p.keywords:
            result.keywords = p.keywords
        if result.is_open_access is None and p.is_open_access is not None:
            result.is_open_access = p.is_open_access
        if not result.source and p.source:
            result.source = p.source
    result.journal_abbr = abbreviate(result.journal)
    return result
