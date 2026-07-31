from __future__ import annotations

from urllib.parse import quote

from ..models.paper import Paper
from ..utils.http import HttpClient


class SemanticScholarConnector:
    def __init__(self, client: HttpClient, api_key: str | None = None):
        self.client = client
        self.api_key = api_key

    def fetch(self, doi: str) -> tuple[Paper | None, dict]:
        fields = "paperId,title,authors,year,venue,abstract,openAccessPdf,url,externalIds"
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        data = self.client.get_json(
            f"https://api.semanticscholar.org/graph/v1/paper/DOI:{quote(doi, safe='')}",
            params={"fields": fields}, headers=headers,
        )
        if not data:
            return None, {}
        pdf = data.get("openAccessPdf") or {}
        paper = Paper(
            doi=doi, title=data.get("title", "") or "",
            authors=[a.get("name", "") for a in data.get("authors", []) if a.get("name")],
            journal=data.get("venue", "") or "", year=data.get("year"),
            abstract=data.get("abstract", "") or "", semantic_scholar_id=data.get("paperId", "") or "",
            landing_url=data.get("url", "") or "", pdf_url=pdf.get("url", "") or "",
            is_open_access=bool(pdf.get("url")), source="semantic_scholar",
        )
        return paper, data
