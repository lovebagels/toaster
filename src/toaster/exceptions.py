"""
Exceptions for toaster
"""


class Error(Exception):
    """Base class for other exceptions"""
    pass


class AlreadyInstalled(Error):
    """Raised when a package or bakery is already installed"""
    pass


class NotFound(Error):
    """Raised when a package is not found"""
    pass
