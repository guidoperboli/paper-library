from __future__ import annotations

from urllib.parse import quote

from ..models.paper import Paper
from ..utils.http import HttpClient


def reconstruct_abstract(index: dict | None) -> str:
    if not index:
        return ""
    words = []
    for word, positions in index.items():
        for pos in positions:
            words.append((pos, word))
    return " ".join(word for _, word in sorted(words))


class OpenAlexConnector:
    def __init__(self, client: HttpClient, email: str | None = None):
        self.client = client
        self.email = email

    def fetch(self, doi: str) -> tuple[Paper | None, dict]:
        params = {"mailto": self.email} if self.email else {}
        data = self.client.get_json(f"https://api.openalex.org/works/https://doi.org/{quote(doi, safe='/')}", params=params)
        if not data:
            return None, {}
        primary = data.get("primary_location") or {}
        source = primary.get("source") or {}
        authors = [x.get("author", {}).get("display_name", "") for x in data.get("authorships", [])]
        oa = data.get("open_access") or {}
        best = data.get("best_oa_location") or primary
        paper = Paper(
            doi=doi, title=data.get("title", "") or "", authors=[a for a in authors if a],
            journal=source.get("display_name", "") or "", year=data.get("publication_year"),
            publisher=source.get("host_organization_name", "") or "",
            abstract=reconstruct_abstract(data.get("abstract_inverted_index")),
            keywords=[c.get("display_name", "") for c in data.get("concepts", [])[:12] if c.get("display_name")],
            openalex_id=data.get("id", "") or "", is_open_access=oa.get("is_oa"),
            oa_status=oa.get("oa_status", "") or "", landing_url=best.get("landing_page_url", "") or "",
            pdf_url=best.get("pdf_url", "") or "", source="openalex",
        )
        return paper, data
