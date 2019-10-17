# js-regex

*A compatibility layer to use Javascript regular expressions in Python.*

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

re.compile("^abc$").search("abc\n")  # matches, unlike JS
js_regex.compile("^abc$").search("abc\n")  # does not match
```

Internally, `js_regex.compile()` replaces JS regex syntax which has a different
meaning in Python with whatever *Python* regex syntax has the intended meaning.

**This only works for the `.search()` method** - there is no equivalent to
`.match()` or `.fullmatch()` for Javascript regular expressions.

We also check for constructs which are valid in Python but not JS - such as
named capture groups - and raise an explicit error.  Constructs which are valid
in JS but not Python may also raise an error, because we're still using Python's
`re.compile()` function under the hood!

The following table is adapted from [this larger version](https://web.archive.org/web/20130830063653/http://www.regular-expressions.info:80/refflavors.html),
ommiting other languages and any rows where JS and Python have the same behaviour.

| Feature                               | Javascript    | Python    | Handling
| ---                                   | ---           | ---       | ---
| `\a` (bell)                           | no            | yes       | Converted to JS behaviour
| `\ca`-`\cz` and `\cA`-`\cZ` (control characters) | yes | no       | Converted to JS behaviour
| `\d` for digits, `\w` for word chars, `\s` for whitespace | ascii | unicode | Converted to JS behaviour (including `\D`, `\W`, `\S` for negated classes)
| `$` (end of line/string)              | at end        | allows trailing `\n` | Converted to JS behaviour
| `\A` (start of string)                | no            | yes       | Explicit error, use `^` instead
| `\Z` (end of string)                  | no            | yes       | Explicit error, use `$` instead
| `(?<=text)` (positive lookbehind)     | new in ES2018 | yes       | Allowed
| `(?<!text)` (negative lookbehind)     | new in ES2018 | yes       | Allowed
| `(?(1)then\|else)`                    | no            | yes       | Explicit error
| `(?(group)then\|else)`                | no            | yes       | Explicit error
| `(?#comment)`                         | no            | yes       | Explicit error
| `(?P<name>regex)` (Python named capture group) | no   | yes       | Not detected (yet)
| `(?P=name)` (Python named backreference) | no         | yes       | Not detected (yet)
| `(?<name>regex)` (JS named capture group) | new in ES2018 | no    | Error from Python, not translated (yet)
| `$<name>` (JS named backreference)    | new in ES2018 | no        | Error from Python, not translated (yet)
| `(?i)` (case insensitive)             | `/i` only     | yes       | Explicit error, compile with `flags=re.IGNORECASE` instead
| `(?m)` (`^` and `$` match at line breaks) | `/m` only | yes       | Explicit error, compile with `flags=re.MULTILINE` instead
| `(?s)` (dot matches newlines)         | no            | yes       | Explicit error, compile with `flags=re.DOTALL` instead
| `(?x)` (free-spacing mode)            | no            | yes       | Explicit error, there is no corresponding mode in Javascript
| Backreferences non-existent groups are an error | no  | yes       | Follows Python behaviour
| Backreferences to failed groups also fail | no        | yes       | Follows Python behaviour
| Nested references `\1` through `\9`   | yes           | no        | Follows Python behaviour

Note that in many cases Python-only regex features would be treated as part of
an ordinary pattern by JS regex engines.  Currently we raise an explicit error
on such inputs, but may translate them to have the JS behaviour in a future version.


## Changelog

#### 1.0.1 - 2019-10-17
- Allow use of native strings on Python 2.  This is not actually valid according
  to the spec, but it's only going to be around for a few months so whatever.

#### 1.0.0 - 2019-10-04
- Now considered feature-complete and stable, as all constructs recommended
  for `jsonschema` patterns are supported and all Python-side incompatibilities
  are detected.
- Compiled patterns are now cached on Python 3, exactly as for `re.compile`

#### 0.4.0 - 2019-10-03
- Now compatible with Python 2.7 and 3.5, until
  [their respective EOL dates](https://devguide.python.org/#status-of-python-branches).

#### 0.3.0 - 2019-09-30
- Fixed handling of non-trailing `$`, e.g. in `"^abc$|^def$"` both are converted
- Added explicit errors for `re.LOCALE` and `re.VERBOSE` flags, which have no JS equivalent
- Added explicit checks and errors for use of Python-only regex features

#### 0.2.0 - 2019-09-28
Convert JS-only syntax to Python equivalent wherever possible.

#### 0.1.0 - 2019-09-28
Initial release, with project setup and a very basic implementation.
