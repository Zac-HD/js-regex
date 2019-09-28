# js-regex

*A thin compatibility layer to use Javascript regular expressions in Python.*

Did you know that regular expressions may vary between programming languages?
For example, let's consider the pattern `"^abc$"`, which matches the string
`"abc"`.  But what about the string `"abc\n"`?  It's also matched in Python,
but not in Javascript!

This and other slight differences can be really important for cross-language
standards like `jsonschema`, and that's why `js-regex` exists.

## How it works

```python
import re
import js_regex

re.compile("^abc$").match("abc\n")  # matches, unlike JS
js_regex.compile("^abc$").match("abc\n")  # does not match
```

Internally, `js_regex.compile()` replaces JS regex syntax which has a different
meaning in Python with whatever *Python* regex syntax has the intended meaning.

We also check for constructs which are valid in Python but not JS - such as
named capture groups - and raise an explicit error.  Constructs which are valid
in JS but not Python are also an error, because we're still using Python's
`re.compile()` function under the hood!

The following table is adapted from [this larger version](https://web.archive.org/web/20130830063653/http://www.regular-expressions.info:80/refflavors.html),
ommiting other languages and any rows where JS and Python have the same behaviour.

| Feature                               | Javascript    | Python    | Handling
| ---                                   | ---           | ---       | ---
| `\a` (bell)                           | no            | yes       | Converted to JS behaviour
| `\ca`-`\cz` and `\cA`-`\cZ` (control characters) | yes | no       | Converted to JS behaviour
| `\d` for digits, `\w` for word chars, `\s` for whitespace | ascii | unicode | Converted to JS behaviour (including `\D`, `\W`, `\S` for negated classes)
| `$` (end of line/string)              | at end        | allows trailing `\n` | Converted to JS behaviour
| `\A` (start of string)                | no            | yes       | TODO: explicit error, suggest `^`
| `\Z` (end of string)                  | no            | yes       | TODO: explicit error, suggest `$`
| `(?<=text)` (positive lookbehind)     | no            | yes       | TODO: explicit error
| `(?<!text)` (negative lookbehind)     | no            | yes       | TODO: explicit error
| `(?(1)then\|else)`                    | no            | yes       | TODO: explicit error
| `(?(group)then\|else)`                | no            | yes       | TODO: explicit error
| `(?#comment)`                         | no            | yes       | TODO: explicit error
| `(?P<name>regex)` (named capture group) | no          | yes       | TODO: explicit error
| `(?P=name)` (named backreference)     | no            | yes       | TODO: explicit error
| Free-spacing / multi-line syntax      | no            | yes       | TODO: explicit error
| `(?s)` (dot matches newlines)         | no            | yes       | TODO: explicit error
| `(?x)` (free-spacing mode)            | no            | yes       | TODO: explicit error
| `(?i)` (case insensitive)             | `/i` only     | yes       | TODO: ???
| `(?m)` (`^` and `$` match at line breaks) | `/m` only | yes       | TODO: ???
| Backreferences non-existent groups are an error | no  | yes       | Follows Python behaviour
| Backreferences to failed groups also fail | no        | yes       | Follows Python behaviour
| Nested references `\1` through `\9`   | yes           | no        | Follows Python behaviour


## Changelog

#### 0.2.0 - 2019-09-28
Convert JS-only syntax to Python equivalent wherever possible.

#### 0.1.0 - 2019-09-28
Initial release, with project setup and a very basic implementation.
