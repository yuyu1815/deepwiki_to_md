class ExtractorError(Exception):
    """Base class for extraction-related errors."""
    pass


class HTTPError(ExtractorError):
    """Errors related to HTTP communication."""
    def __init__(self, url: str, status_code: int, message: str):
        self.url = url
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message} for {url}")


class ContentError(ExtractorError):
    """Errors related to content processing."""
    pass


class ConfigError(ExtractorError):
    """Errors related to configuration."""
    pass
