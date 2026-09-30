from __future__ import annotations

import re
from urllib.parse import quote

from ..utils.http import HttpClient


class SciHubConnector:
    def __init__(self, client: HttpClient, base_url: str = "https://sci-hub.ru"):
        self.client = client
        self.base_url = base_url.rstrip("/")

    def get_pdf_url(self, doi: str) -> str | None:
        url = f"{self.base_url}/{quote(doi, safe='')}"
        # We spoof a regular browser just in case
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36", "Cookie": "__ddg1_=aoIUA3LRLWQmJZxo1MrM; session=ac0fc6114b2d4e0f361c9f7a482bc783; __ddg9_=94.33.15.206; PHPSESSID=fa19b05a417242fba3bc5acb967ae54d; refresh=1790756413.8611; __ddg10_=1790756445; __ddg8_=WVTvqoQhobJv1C8s"}
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = self.client.get(url, headers=headers, verify=False)
            if not response.ok:
                return None
            
            html = response.text
            # Sci-hub usually uses an iframe with id="pdf" or an embed tag
            # e.g., <iframe src="//moscow.sci-hub.se/123/456.pdf#navpanes=0&view=FitH" id="pdf"></iframe>
            # or <embed type="application/pdf" src="..." id="pdf">
            match = re.search(r"<iframe[^>]+src\s*=\s*['\"](.*?)['\"]", html, re.IGNORECASE)
            if not match:
                match = re.search(r"<embed[^>]+src\s*=\s*['\"](.*?)['\"]", html, re.IGNORECASE)
            if not match:
                match = re.search(r"<object[^>]+data\s*=\s*['\"](.*?)['\"]", html, re.IGNORECASE)
            
            if match:
                pdf_src = match.group(1).split("#")[0]  # remove hash fragments
                if pdf_src.startswith("//"):
                    return f"https:{pdf_src}"
                elif pdf_src.startswith("/"):
                    return f"{self.base_url}{pdf_src}"
                return pdf_src
        except Exception:
            pass
            
        return None
