# utils/exceptions.py

class ScraperError(Exception):
    """Base exception for all scraper errors"""


class NetworkError(ScraperError):
    """HTTP / connection failures"""


class CaseParsingError(ScraperError):
    """Failure while parsing case list or case detail page"""


class DocketParsingError(ScraperError):
    """Failure while extracting docket entries"""


class PDFDownloadError(ScraperError):
    """PDF could not be downloaded"""


class PDFExtractionError(ScraperError):
    """PDF text extraction failed"""


class PhoneNotFound(ScraperError):
    """No phone number located in any eligible document"""
