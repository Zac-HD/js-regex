"""The implementation of the js-regex library."""
from __future__ import unicode_literals

import re
import sre_constants
import sre_parse
from sys import version_info as python_version

try:
    from functools import lru_cache
    from typing import Any, Pattern  # pragma: no cover  # for Python 2
except ImportError:  # pragma: no cover

    def lru_cache(maxsize):  # type: ignore
        return lambda f: f


class NotJavascriptRegex(ValueError):
    """The pattern uses Python regex features that do not exist in Javascript."""


if python_version.major < 3:  # pragma: no cover  # Awful Python 2 compat hack.
    exec("chr = unichr")  # nosec


@lru_cache(maxsize=512)  # Matches the internal cache size for re.compile
def compile(pattern, flags=0):
    # type: (str, int) -> Pattern[str]
    """Compile the given string, treated as a Javascript regex.

    This aims to match all strings that would be matched in JS, and as few
    additional strings as possible.  Where possible it will also warn if the
    pattern would not be valid in JS.

    This is not a full implementation of EMCA-standard regex, but somewhat
    better than simply ignoring the differences between dialects.
    """
    if not isinstance(pattern, (str, type(""))):
        raise TypeError("pattern={!r} must be a unicode string".format(pattern))
    if not isinstance(flags, int):
        raise TypeError("flags={!r} must be an integer".format(flags))
    # Check that the supplied flags are legal in both Python and JS.  See
    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp#Parameters
    # and the list of flags at https://docs.python.org/3/library/re.html#re.compile
    if flags & re.LOCALE:
        raise NotJavascriptRegex("The re.LOCALE flag has no equivalent in Javascript")
    if flags & re.TEMPLATE:
        raise NotJavascriptRegex("The re.TEMPLATE flag has no equivalent in Javascript")
    if flags & re.VERBOSE:
        raise NotJavascriptRegex("The re.VERBOSE flag has no equivalent in Javascript")

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
        parsed = sre_parse.parse(pattern, flags=flags)
    except re.error as e:
        raise re.error("{} in pattern={!r}".format(e, pattern))
    check_features(parsed, flags=flags, pattern=pattern)
    # Check for comments - with `in` because don't appear in the parse tree.
    if re.search(r"\(\?\#[^)]*\)", pattern):
        raise NotJavascriptRegex(
            "'(?#comment)' groups are ignored by Python, but have no meaning in "
            "Javascript regular expressions (pattern={!r})".format(pattern)
        )
    # Replace any unescaped $ - which is allowed in both but behaves
    # differently - with the Python-only \Z which behaves like JS' $.
    pattern = re.sub(r"(?<!\\)[$]", repl=r"\\Z", string=pattern)
    # Finally, we compile our fixed pattern to a Python regex pattern and return it.
    return re.compile(pattern, flags=flags)


def check_features(parsed, flags, pattern):
    # type: (Any, int, str) -> None
    """Recursively walk through a SRE regex parse tree to check that every
    node is for a feature that also exists in Javascript regular expressions.

    `parsed` is either a list of SRE regex elements representations or a
    particular element representation. Each element is a tuple of element code
    (as string) and parameters. E.g. regex 'ab[0-9]+' compiles to following
    elements:

        [
            (LITERAL, 97),
            (LITERAL, 98),
            (MAX_REPEAT, (1, 4294967295, [
                (IN, [
                    (RANGE, (48, 57))
                ])
            ]))
        ]

    This function is inspired by https://github.com/HypothesisWorks/hypothesis
    /blob/master/hypothesis-python/src/hypothesis/searchstrategy/regex.py
    """
    if not isinstance(parsed, tuple):
        for elem in parsed:
            assert isinstance(elem, tuple)
            check_features(elem, flags=flags, pattern=pattern)
    else:
        code, value = parsed
        if code == sre_constants.ASSERT or code == sre_constants.ASSERT_NOT:
            # Regexes '(?=...)', '(?<=...)', '(?!...)' or '(?<!...)'
            # (positive/negative lookahead/lookbehind)
            check_features(value[1], flags=flags, pattern=pattern)
        elif code == sre_constants.MIN_REPEAT or code == sre_constants.MAX_REPEAT:
            # Regexes 'a?', 'a*', 'a+', and their non-greedy variants (repeaters)
            check_features(value[2], flags=flags, pattern=pattern)
        elif code == sre_constants.BRANCH:
            # Regex 'a|b|c' (branch)
            for branch in value[1]:
                check_features(branch, flags=flags, pattern=pattern)
        elif code == sre_constants.SUBPATTERN:
            # Various groups: '(...)', '(:...)' or '(?P<name>...)'
            # The parser converts group names to numbers, so the `_` doesn't help here
            check_features(value[-1], flags=flags, pattern=pattern)
            if python_version >= (3, 6) and (value[1] | value[2]):  # pragma: no cover
                raise NotJavascriptRegex(
                    "Javascript regular expressions do not support "
                    "subpattern flags (pattern={pattern!r})"
                )
        elif code == sre_constants.AT:
            # Regexes like '^...', '...$', '\bfoo', '\Bfoo', '\A', '\Z'
            if value == sre_constants.AT_BEGINNING_STRING:
                raise NotJavascriptRegex(
                    r"\A is not valid in Javascript regular expressions - "
                    "use ^ instead (pattern={!r})".format(pattern)
                )
            if value == sre_constants.AT_END_STRING:
                raise NotJavascriptRegex(
                    r"\Z is not valid in Javascript regular expressions - "
                    "use $ instead (pattern={!r})".format(pattern)
                )
        elif code == sre_constants.GROUPREF_EXISTS:
            # Regex '(?(id/name)yes-pattern|no-pattern)' (if group exists choice)
            raise NotJavascriptRegex(
                "Javascript regular expressions do not support if-group-exists choice, "
                "like `'(?(id/name)yes-pattern|no-pattern)'` (pattern={!r})".format(
                    pattern
                )
            )
        else:
            assert code in [
                sre_constants.IN,  # Regex '[abc0-9]' (set of characters)
                sre_constants.ANY,  # Regex '.' (any char)
                sre_constants.LITERAL,  # Regex 'a' (single char)
                sre_constants.NOT_LITERAL,  # Regex '[^a]' (negation of a single char)
                sre_constants.GROUPREF,  # Regex '\\1' or '(?P=name)' (group reference)
            ]
