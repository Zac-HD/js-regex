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
    # TODO: validate input types
    # TODO: validate flags range
    if pattern.endswith("$"):
        pattern = pattern[:-1] + r"\Z"
    # TODO: fix other incompatibilties e.g. \d
    # TODO: detect Python-only constructs
    return re.compile(pattern, flags=flags)
