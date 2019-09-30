"""Tests for the js-regex library."""

import re

import pytest

import js_regex


@pytest.mark.parametrize(
    "pattern,good_match,bad_match",
    [
        ("^abc", "abc", ""),
        ("^abc", "abcd", "not abc"),
        ("^abc$", "abc", "abc\n"),
        ("^abc$|^def$", "abc", "abc\n"),
        ("^abc$|^def$", "def", "def\n"),
        (r"^abc\$", "abc$", "abc"),
        (r"\a", "\a", r"\a"),
        (r"\cA", "\x01", r"\cA"),
        (r"\ca", "\x01", r"\ca"),
    ],
)
def test_expected_transforms(pattern, good_match, bad_match):
    regex = js_regex.compile(pattern)
    assert regex.match(good_match)
    assert not regex.match(bad_match)


@pytest.mark.parametrize(
    "pattern,good_match,bad_match",
    [
        (r"\d", "1", "߀"),  # NKO DIGIT ZERO
        (r"\D", "߀", "1"),
        (r"\w", "a", "é"),  # e-acute
        (r"\W", "é", "a"),
        (r"\s", "\t", "\xa0"),  # non-breaking space
        (r"\S", "\xa0", "\t"),
    ],
)
def test_charclass_transforms(pattern, good_match, bad_match):
    regex = js_regex.compile(pattern)
    assert regex.match(good_match)
    assert not regex.match(bad_match)
    if ord(bad_match) >= 128:
        # Non-ascii string is matched by Python, but not in JS mode
        assert re.compile(pattern).match(bad_match)


@pytest.mark.parametrize(
    "flags,error",
    [
        ("flags", TypeError),
        (re.LOCALE, js_regex.NotJavascriptRegex),
        (re.TEMPLATE, js_regex.NotJavascriptRegex),
        (re.VERBOSE, js_regex.NotJavascriptRegex),
    ],
)
def test_flags_validation(flags, error):
    with pytest.raises(error):
        js_regex.compile("", flags=flags)


@pytest.mark.parametrize(
    "pattern,flags,error",
    [(1, 0, TypeError), ("abc", "flags", TypeError), ("(abc(", 0, ValueError)],
)
def test_input_validation(pattern, flags, error):
    with pytest.raises(error):
        js_regex.compile(pattern, flags=flags)
