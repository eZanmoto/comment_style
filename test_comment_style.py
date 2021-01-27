# Copyright 2021 Sean Kelleher. All rights reserved.
# Use of this source code is governed by an MIT
# licence that can be found in the LICENCE file.

# `$0` runs tests to validate the behaviour of `comment_style.py`.

import sys

import comment_style


# `(` and `)` are used to explicitly mark the beginning and end of string
# sections.
TESTS = [
    "",
    "x",
    "'(",
    # String escaping is only considered valid within a string.
    "\\'(",
    "\\\\'(",
    "'()'",
    "'(a)'",
    "x = '()'",
    "x = '(a)'",
    "x = '(\\'",
    "x = '(\\n)'",
    "x = '(\\n\\'",
    "x = '(\\\\)'",
    "x = '(\\\\n)'",
    "x = '(\\\\\\'",
]


def main():
    if len(sys.argv) != 1:
        print("usage: {0}".format(sys.argv[0]))
        sys.exit(1)
    test_is_likely_in_str(TESTS)


def test_is_likely_in_str(tests):
    all_passed = True
    for i, test in enumerate(tests):
        for j, exp in enumerate(is_in_strs(test)):
            src = test.replace('(', '').replace(')', '')
            act = comment_style.is_likely_in_str(src, j)
            if exp != act:
                print(
                    "Test {}: \"{}\": expected '{}' but got '{}'"
                        .format(i + 1, src[:j], exp, act),
                )
                all_passed = False
                break
    if all_passed:
        print("All tests passed")
    else:
        sys.exit(1)


def is_in_strs(src):
    """
        Return a list with an element for each boundary in `src`, where each
        element is `True` if it's "inside a string" and `False` otherwise.
        
        The beginning of a string section in `src` should be marked with `(`
        and the end marked with `)`. However, note that the difference between
        the two markers is purely stylistic, and the same result will be
        produced regardless of the marker being used.

        >>> is_in_strs("")
        [False]
        >>> is_in_strs("x")
        [False, False]
        >>> is_in_strs("'(")
        [False, True]
        >>> is_in_strs("'()'")
        [False, True, False]
        >>> is_in_strs("'(a)'")
        [False, True, True, False]
        >>> is_in_strs("x = '(a)'")
        [False, False, False, False, False, True, True, False]
    """
    in_str = False
    in_strs = [in_str]
    for substr in src.replace(")", "(").split("("):
        mod = 1 if in_str else -1
        in_strs += [in_str] * (len(substr) + mod)
        in_str = not in_str
    if len(src) != 0 and in_str:
        in_strs += [False]
    return in_strs


if __name__ == '__main__':
    main()
