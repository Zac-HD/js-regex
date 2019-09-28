"""Tests for the js-regex library."""

import pytest

import js_regex

DATA = [
    # (pattern, [should match], [should not match])
    ("^abc", ["abc", "abcd"], ["not abc"]),
    ("^abc$", ["abc"], ["abc\n"]),
]


@pytest.mark.parametrize("pattern,good_match,bad_match", DATA)
def test_expected_transforms(pattern, good_match, bad_match):
    regex = js_regex.compile(pattern)
    for string in good_match:
        assert regex.match(string)
    for string in bad_match:
        assert not regex.match(string)


@pytest.mark.parametrize(
    "pattern,flags,error",
    [(1, 0, TypeError), ("abc", "flags", TypeError), ("(abc(", 0, ValueError)],
)
def test_input_validation(pattern, flags, error):
    with pytest.raises(error):
        js_regex.compile(pattern, flags=flags)
