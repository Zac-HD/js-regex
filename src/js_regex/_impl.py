"""The implementation of the js-regex library."""

import re
from typing import Pattern


def compile(pattern: str, *, flags: int = 0) -> Pattern[str]:
    """Compile the given string, treated as a Javascript regex.

    This aims to match all strings that would be matched in JS, and as few
    additional strings as possible.  Where possible it will also warn if the
    pattern would not be valid in JS.

    This is not a full implementation of EMCA-standard regex, but somewhat
    better than simply ignoring the differences between dialects.
    """
    if not isinstance(pattern, str):
        raise TypeError(f"pattern={pattern!r} must be a string")
    if not isinstance(flags, int):
        raise TypeError(f"flags={flags!r} must be an integer")
    # TODO: validate flags range
    # TODO: replace JS-only with Python-compatible constructs
    try:
        re.compile(pattern)
    except Exception:
        raise ValueError(f"pattern={pattern!r} is not a valid regular expression")
    if pattern.endswith("$") and not pattern.endswith(r"\$"):
        pattern = pattern[:-1] + r"\Z"
    # TODO: fix other incompatibilties e.g. \d
    # TODO: detect Python-only constructs
    return re.compile(pattern, flags=flags)
