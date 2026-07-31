from __future__ import annotations

import re

DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)


def normalize_doi(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", value, flags=re.I)
    match = DOI_RE.search(value)
    if not match:
        raise ValueError(f"Invalid DOI: {value}")
    return match.group(0).rstrip(".,;)").lower()
