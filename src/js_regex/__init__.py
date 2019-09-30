"""A thin compatibility layer to use Javascript regular expressions in Python."""

__version__ = "0.3.0"
__all__ = ["NotJavascriptRegex", "compile"]

from ._impl import NotJavascriptRegex, compile
