from typing import Any, Dict, Optional
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from deepwiki.core.config import HTTPConfig
from deepwiki.core.errors import HTTPError


class HTTPClient:
    """HTTP communication handling class

    Maintenance notes (for yourself in 6 months):
    - Add proxy support to __init__
    - Implement authentication in _create_request()
    - Add caching layer to fetch_url()
    """

    def __init__(
        self,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.timeout = timeout or HTTPConfig.DEFAULT_TIMEOUT
        self.headers = headers or HTTPConfig.DEFAULT_HEADERS.copy()

    def fetch_url(self, url: str) -> str:
        """Fetch HTML from URL (with error handling)"""
        if not self._is_valid_url(url):
            raise HTTPError(url, 0, "Invalid URL format")

        request = self._create_request(url)

        try:
            with urlopen(request, timeout=self.timeout) as response:
                return self._process_response(response)
        except Exception as e:
            raise HTTPError(url, 0, str(e))

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and security"""
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)

    def _create_request(self, url: str) -> Request:
        """Create HTTP request with appropriate headers"""
        return Request(url, headers=self.headers)

    def _process_response(self, response: Any) -> str:
        """Process HTTP response and decode considering encoding.

        Keep nesting shallow by separating decompression into small functions,
        ensuring readability with early returns (guard clauses).
        """
        data = response.read()

        def _decompress(data_bytes: bytes, enc: str) -> bytes:
            enc = (enc or "").lower().strip()
            if not enc:
                return data_bytes

            # gzip / x-gzip
            if enc in ("gzip", "x-gzip"):
                try:
                    import gzip

                    return gzip.decompress(data_bytes)
                except Exception:
                    return data_bytes

            # deflate (zlib/raw)
            if enc == "deflate":
                try:
                    import zlib

                    return zlib.decompress(data_bytes)
                except Exception:
                    try:
                        import zlib as _z

                        return _z.decompress(data_bytes, -_z.MAX_WBITS)
                    except Exception:
                        return data_bytes

            return data_bytes

        # Handle compression
        data = _decompress(data, response.headers.get("Content-Encoding"))

        # Determine charset
        charset = response.headers.get_content_charset() or "utf-8"
        try:
            return data.decode(charset, errors="replace")
        except LookupError:
            return data.decode("utf-8", errors="replace")
