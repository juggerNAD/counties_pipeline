class ScraperError(Exception):
    pass

class PDFNotFoundError(ScraperError):
    pass

class PhoneNotFoundError(ScraperError):
    pass
