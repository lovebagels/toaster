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


class UseNotFound(Error):
    """Raised when a use dependency is not found"""
    pass


class DependedOnError(Error):
    """Raised when a package cannot be removed because it is depended on by other packages"""

    def ___init__(self, message, dependants):
        super().__init__(message)
        self.msg = message
        self.dependants = []
