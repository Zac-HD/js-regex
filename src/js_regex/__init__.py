"""A thin compatibility layer to use Javascript regular expressions in Python."""

__version__ = "0.1.0"
__all__ = ["compile"]

from ._impl import compile
