from __future__ import absolute_import, print_function, unicode_literals


class Error(Exception):
    """Simple base error for the package."""

    pass


class AuthenticationError(Error):
    """AuthenticationError indicates either invalid or expired credentials."""

    pass


class TimeoutError(AuthenticationError):
    """Invalid authentication timestamp."""

    pass
