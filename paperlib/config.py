from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    api_key: str | None
    inst_token: str | None
    unpaywall_email: str | None
    crossref_email: str | None
    semantic_scholar_api_key: str | None
    library_dir: Path
    timeout: int
    delay: float
    max_workers: int
    user_agent: str

    @classmethod
    def load(cls, env_file: str | Path | None = None) -> "Settings":
        load_dotenv(env_file or Path.cwd() / ".env")
        library_dir = Path(os.getenv("PAPER_LIBRARY_DIR", "papers")).expanduser()
        email = os.getenv("CROSSREF_EMAIL") or os.getenv("UNPAYWALL_EMAIL")
        return cls(
            api_key=os.getenv("ELSEVIER_API_KEY") or None,
            inst_token=os.getenv("ELSEVIER_INST_TOKEN") or None,
            unpaywall_email=os.getenv("UNPAYWALL_EMAIL") or None,
            crossref_email=os.getenv("CROSSREF_EMAIL") or email,
            semantic_scholar_api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY") or None,
            library_dir=library_dir,
            timeout=int(os.getenv("REQUEST_TIMEOUT", "60")),
            delay=float(os.getenv("DOWNLOAD_DELAY", "0.5")),
            max_workers=max(1, int(os.getenv("MAX_WORKERS", "4"))),
            user_agent=os.getenv("USER_AGENT", f"PaperLibrary/3.0 (mailto:{email or 'unknown@example.org'})"),
        )

    def ensure_dirs(self) -> None:
        for path in [
            self.library_dir,
            self.library_dir / "pdf",
            self.library_dir / "metadata",
            self.library_dir / "metadata" / "scopus",
            self.library_dir / "metadata" / "crossref",
            self.library_dir / "metadata" / "unpaywall",
            self.library_dir / "metadata" / "openalex",
            self.library_dir / "metadata" / "semantic_scholar",
            self.library_dir / "logs",
        ]:
            path.mkdir(parents=True, exist_ok=True)
