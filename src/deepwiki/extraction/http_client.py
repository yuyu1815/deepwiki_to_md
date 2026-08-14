import socket
from typing import Any, Dict, Optional
from urllib.error import HTTPError as UrllibHTTPError
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from deepwiki.core.config import HTTPConfig
from deepwiki.core.errors import HTTPError


class HTTPClient:
    """Fetch and decode HTTP content."""

    def __init__(
        self,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.timeout = HTTPConfig.DEFAULT_TIMEOUT if timeout is None else timeout
        self.headers = HTTPConfig.DEFAULT_HEADERS.copy() if headers is None else headers

    def fetch_url(self, url: str) -> str:
        """Fetch HTML from an HTTP or HTTPS URL."""
        if not self._is_valid_url(url):
            raise HTTPError(url, 0, "Invalid URL format")

        try:
            with urlopen(self._create_request(url), timeout=self.timeout) as response:
                return self._process_response(response)
        except UrllibHTTPError as exc:
            raise HTTPError(url, exc.code, str(exc.reason)) from exc
        except (URLError, socket.timeout, TimeoutError) as exc:
            raise HTTPError(url, 0, str(exc)) from exc
        except OSError as exc:
            raise HTTPError(url, 0, str(exc)) from exc

    def _is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)

    def _create_request(self, url: str) -> Request:
        return Request(url, headers=self.headers)

    def _process_response(self, response: Any) -> str:
        data = self._decompress(
            response.read(), response.headers.get("Content-Encoding")
        )
        charset = response.headers.get_content_charset() or "utf-8"
        try:
            return data.decode(charset, errors="replace")
        except LookupError:
            return data.decode("utf-8", errors="replace")

    @staticmethod
    def _decompress(data: bytes, encoding: str) -> bytes:
        encoding = (encoding or "").lower().strip()
        if encoding in ("gzip", "x-gzip"):
            import gzip

            try:
                return gzip.decompress(data)
            except (OSError, EOFError):
                return data
        if encoding == "deflate":
            import zlib

            try:
                return zlib.decompress(data)
            except zlib.error:
                try:
                    return zlib.decompress(data, -zlib.MAX_WBITS)
                except zlib.error:
                    return data
        return data
