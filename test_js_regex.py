"""Tests for the js-regex library."""

import pytest

from js_regex import compile

DATA = [
    # (pattern, [should match], [should not match])
    ("^abc", ["abc", "abcd"], ["not abc"]),
    ("^abc$", ["abc"], ["abc\n"]),
]


@pytest.mark.parametrize("pattern,good_match,bad_match", DATA)
def test_expected_transforms(pattern, good_match, bad_match):
    regex = compile(pattern)
    for string in good_match:
        assert regex.match(string)
    for string in bad_match:
        assert not regex.match(string)
