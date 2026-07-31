from __future__ import annotations

import time
from typing import Any

import requests


class HttpClient:
    def __init__(self, timeout: int, user_agent: str, delay: float = 0.0):
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        if self.delay:
            time.sleep(self.delay)
        response = self.session.get(url, timeout=self.timeout, **kwargs)
        return response

    def get_json(self, url: str, **kwargs: Any) -> dict[str, Any] | None:
        response = self.get(url, **kwargs)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
