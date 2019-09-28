"""The implementation of the js-regex library."""

import re
from functools import lru_cache
from typing import Pattern


@lru_cache()
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
    # Replace JS-only BELL escape with BELL character, and replace character class
    # shortcuts (Unicode in Python) with the corresponding ASCII set like in JS.
    for esc, replacement in [
        (r"\a", "\a"),
        (r"\d", "[0-9]"),
        (r"\D", "[^0-9]"),
        (r"\w", "[A-Za-z]"),
        (r"\W", "[^A-Za-z]"),
        (r"\s", "[ \t\n\r\x0b\x0c]"),
        (r"\S", "[^ \t\n\r\x0b\x0c]"),
    ]:
        # r"(?<!\\)" is 'not preceeded by a backslash', i.e. the escape is unescaped.
        pattern = re.sub(r"(?<!\\)" + re.escape(esc), repl=replacement, string=pattern)
    # Replace JS-only control-character escapes \cA - \cZ and \ca - \cz
    # with their corresponding control characters.
    pattern = re.sub(
        r"(?<!\\)(\\c[A-Za-z])",
        repl=lambda m: chr(ord(m.group(0)[-1].upper()) - 64),
        string=pattern,
    )
    # Compile at this stage, to check for Python-only constructs *before* we add any.
    try:
        rgx = re.compile(pattern, flags=flags)
    except Exception:
        raise ValueError(f"pattern={pattern!r} is not a valid regular expression")
    assert rgx  # TODO: implement those checks
    # Replace any trailing unescaped $ - which is allowed in both but behaves
    # differently - with the Python-only \Z which behaves like JS' $.
    if pattern.endswith("$") and not pattern.endswith(r"\$"):
        pattern = pattern[:-1] + r"\Z"
    # Finally, we compile our fixed pattern to a Python regex pattern and return it.
    return re.compile(pattern, flags=flags)
