from __future__ import annotations

from urllib.parse import quote

from ..models.paper import Paper
from ..utils.http import HttpClient


class ElsevierConnector:
    def __init__(self, client: HttpClient, api_key: str | None, inst_token: str | None = None):
        self.client = client
        self.api_key = api_key
        self.inst_token = inst_token

    @property
    def headers(self) -> dict[str, str]:
        headers = {}
        if self.api_key:
            headers["X-ELS-APIKey"] = self.api_key
        if self.inst_token:
            headers["X-ELS-Insttoken"] = self.inst_token
        return headers

    def fetch_scopus(self, doi: str) -> tuple[Paper | None, dict]:
        if not self.api_key:
            return None, {}
        url = f"https://api.elsevier.com/content/abstract/doi/{quote(doi, safe='')}"
        data = self.client.get_json(url, params={"view": "FULL"}, headers={**self.headers, "Accept": "application/json"})
        if not data:
            return None, {}
        core = data.get("abstracts-retrieval-response", {}).get("coredata", {})
        authors_data = data.get("abstracts-retrieval-response", {}).get("authors", {}).get("author", [])
        authors = []
        for a in authors_data:
            name = a.get("ce:indexed-name") or " ".join([a.get("ce:given-name", ""), a.get("ce:surname", "")]).strip()
            if name:
                authors.append(name)
        year = None
        date = core.get("prism:coverDate", "")
        if date[:4].isdigit():
            year = int(date[:4])
        paper = Paper(
            doi=doi, title=core.get("dc:title", "") or "", authors=authors,
            journal=core.get("prism:publicationName", "") or "", year=year,
            publisher=core.get("dc:publisher", "") or "", abstract=core.get("dc:description", "") or "",
            scopus_id=(core.get("dc:identifier", "") or "").replace("SCOPUS_ID:", ""),
            landing_url=core.get("prism:url", "") or "", source="scopus",
        )
        return paper, data

    def download_document(self, doi: str, destination, format="json") -> tuple[bool, str]:
        if not self.api_key:
            return False, "missing_api_key"
        url = f"https://api.elsevier.com/content/article/doi/{quote(doi, safe='')}"
        accept = "application/json" if format == "json" else "application/pdf"
        params = {"httpAccept": accept}
        if format == "json":
            params["view"] = "FULL"
        response = self.client.get(url, params=params, headers={**self.headers, "Accept": accept}, stream=True)
        if response.status_code in (401, 403):
            return False, "not_entitled"
        if response.status_code == 404:
            return False, "not_found"
        try:
            response.raise_for_status()
        except Exception as exc:
            return False, f"http_error_{response.status_code}"
        iterator = response.iter_content(65536)
        first = next(iterator, b"")
        ctype = response.headers.get("Content-Type", "").lower()
        if format == "pdf" and not (first.startswith(b"%PDF") or "application/pdf" in ctype):
            return False, "not_pdf"
        elif format == "json" and "application/json" not in ctype:
            return False, "not_json"
            
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as fh:
            fh.write(first)
            for chunk in iterator:
                if chunk:
                    fh.write(chunk)
        return True, "downloaded"
