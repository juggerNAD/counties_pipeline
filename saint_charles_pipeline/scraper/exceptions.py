"""
Custom exceptions for Missouri Case.net Probate Scraper
"""

class ScraperError(Exception):
    """Base scraper exception"""
    pass


class SessionInitError(ScraperError):
    """Raised when HTTP session cannot be initialized"""
    pass


class SearchError(ScraperError):
    """Raised when case search fails"""
    pass


class CaseParseError(ScraperError):
    """Raised when case list parsing fails"""
    pass


class CaseDetailError(ScraperError):
    """Raised when case detail page fails to load"""
    pass


class DocketParseError(ScraperError):
    """Raised when docket entries cannot be parsed"""
    pass


class PDFDownloadError(ScraperError):
    """Raised when PDF download fails"""
    pass


class PDFParseError(ScraperError):
    """Raised when PDF text extraction fails"""
    pass

