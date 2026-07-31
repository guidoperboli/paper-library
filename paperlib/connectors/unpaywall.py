from __future__ import annotations

from urllib.parse import quote

from ..models.paper import Paper
from ..utils.http import HttpClient


class UnpaywallConnector:
    def __init__(self, client: HttpClient, email: str | None):
        self.client = client
        self.email = email

    def fetch(self, doi: str) -> tuple[Paper | None, dict]:
        if not self.email:
            return None, {}
        data = self.client.get_json(
            f"https://api.unpaywall.org/v2/{quote(doi, safe='')}", params={"email": self.email}
        )
        if not data:
            return None, {}
        best = data.get("best_oa_location") or {}
        authors = [a.get("raw_author_name", "") for a in data.get("z_authors") or [] if a.get("raw_author_name")]
        paper = Paper(
            doi=doi, title=data.get("title", "") or "", authors=authors,
            journal=data.get("journal_name", "") or "", year=data.get("year"),
            publisher=data.get("publisher", "") or "", is_open_access=data.get("is_oa"),
            oa_status=data.get("oa_status", "") or "", license=best.get("license", "") or "",
            landing_url=best.get("url_for_landing_page", "") or data.get("doi_url", "") or "",
            pdf_url=best.get("url_for_pdf", "") or "", source="unpaywall",
        )
        return paper, data
