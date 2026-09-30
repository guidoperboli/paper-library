from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from .config import Settings
from .connectors.crossref import CrossrefConnector
from .connectors.elsevier import ElsevierConnector
from .connectors.openalex import OpenAlexConnector
from .connectors.scihub import SciHubConnector
from .connectors.semantic_scholar import SemanticScholarConnector
from .connectors.unpaywall import UnpaywallConnector
from .database.sqlite import LibraryDB
from .merge import merge_papers
from .models.paper import Paper
from .naming import filename_for, unique_path
from .utils.doi import normalize_doi
from .utils.http import HttpClient


class PaperLibrary:
    def __init__(self, settings: Settings):
        self.settings = settings
        settings.ensure_dirs()
        self.db = LibraryDB(settings.library_dir / "papers.db")
        client = HttpClient(settings.timeout, settings.user_agent, settings.delay)
        self.elsevier = ElsevierConnector(client, settings.api_key, settings.inst_token)
        self.crossref = CrossrefConnector(client, settings.crossref_email)
        self.unpaywall = UnpaywallConnector(client, settings.unpaywall_email)
        self.openalex = OpenAlexConnector(client, settings.crossref_email)
        self.semantic = SemanticScholarConnector(client, settings.semantic_scholar_api_key)
        self.scihub = SciHubConnector(client, settings.scihub_url)

    def _save_raw(self, source: str, doi: str, data: dict) -> str:
        if not data:
            return ""
        path = self.settings.library_dir / "metadata" / source / f"{doi.replace('/', '_')}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)

    def _download_url(self, url: str, destination: Path, verify: bool = True) -> bool:
        if not url:
            return False
        response = self.elsevier.client.get(url, stream=True, allow_redirects=True, verify=verify)
        if not response.ok:
            return False
        iterator = response.iter_content(65536)
        first = next(iterator, b"")
        ctype = response.headers.get("Content-Type", "").lower()
        if not (first.startswith(b"%PDF") or "application/pdf" in ctype):
            return False
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as fh:
            fh.write(first)
            for chunk in iterator:
                if chunk:
                    fh.write(chunk)
        return True

    def process(self, raw_doi: str, overwrite: bool = False) -> Paper:
        doi = normalize_doi(raw_doi)
        old = self.db.get(doi)
        if old and old.get("status") == "downloaded" and old.get("pdf_path") and Path(old["pdf_path"]).exists() and not overwrite:
            p = Paper(doi=doi)
            for key, value in old.items():
                if hasattr(p, key):
                    if key in ("authors", "keywords") and isinstance(value, str):
                        value = [x.strip() for x in value.split(";") if x.strip()]
                    setattr(p, key, value)
            return p
        papers, raw_records = [], []
        for name, connector in [("scopus", self.elsevier), ("crossref", self.crossref), ("unpaywall", self.unpaywall), ("openalex", self.openalex), ("semantic_scholar", self.semantic)]:
            try:
                if name == "scopus":
                    paper, raw = connector.fetch_scopus(doi)
                else:
                    paper, raw = connector.fetch(doi)
                if paper:
                    papers.append(paper)
                if raw:
                    self._save_raw(name, doi, raw)
                    raw_records.append(raw)
            except Exception:
                continue
        paper = merge_papers(doi, papers)
        year_dir = self.settings.library_dir / "papers" / str(paper.year or "unknown")
        target_json = year_dir / filename_for(paper, ext="json")
        target_pdf = year_dir / filename_for(paper, ext="pdf")
        if not overwrite:
            target_json = unique_path(target_json)
            target_pdf = unique_path(target_pdf)
        downloaded = False
        target = target_json
        try:
            downloaded, reason = self.elsevier.download_document(doi, target_json, format="json")
            if downloaded:
                target = target_json
            elif paper.pdf_url:
                downloaded = self._download_url(paper.pdf_url, target_pdf)
                if downloaded:
                    target = target_pdf
                    reason = "downloaded_open_access"
            
            if not downloaded and self.settings.use_scihub:
                scihub_pdf = self.scihub.get_pdf_url(doi)
                if scihub_pdf:
                    downloaded = self._download_url(scihub_pdf, target_pdf, verify=False)
                    if downloaded:
                        target = target_pdf
                        reason = "downloaded_scihub"
            
            paper.status = "downloaded" if downloaded else "metadata_only"
            paper.error = "" if downloaded else reason
            if downloaded:
                paper.pdf_path = str(target)
        except Exception as exc:
            paper.status = "error"
            paper.error = str(exc)
        paper.metadata_path = str(self.settings.library_dir / "metadata")
        self.db.upsert(paper)
        return paper

    def process_many(self, dois: list[str], overwrite: bool = False, workers: int | None = None):
        workers = workers or self.settings.max_workers
        results = []
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(self.process, doi, overwrite): doi for doi in dois}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Papers"):
                try:
                    results.append(future.result())
                except Exception as exc:
                    results.append(Paper(doi=futures[future], status="error", error=str(exc)))
        return results
