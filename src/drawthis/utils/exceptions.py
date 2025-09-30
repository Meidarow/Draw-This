class DrawThisError(Exception):
    """Base class for app exceptions."""


class TextureDecodeError(DrawThisError):
    """Raised when an image cannot be decoded."""


class CrawlerError(DrawThisError):
    """Raised when the crawler fails."""
