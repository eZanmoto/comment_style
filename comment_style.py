# Copyright 2021 Sean Kelleher. All rights reserved.
# Use of this source code is governed by an MIT
# licence that can be found in the LICENCE file.

# `$0 <config-yaml> [--verbose]` outputs issues found in comment blocks
# specified in `config-yaml`. Only the first issue encountered in each comment
# block is output.

import glob
import sys
import yaml


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        fatal("usage: {0} <config-yaml> [--verbose]".format(sys.argv[0]))

    conf_file = sys.argv[1]
    verbose = False
    if len(sys.argv) > 2:
        if sys.argv[2] not in ['-v', '--verbose']:
            fatal("usage: {0} <config-yaml> [--verbose]".format(sys.argv[0]))
        verbose = True

    with open(conf_file) as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)

    paths_rules, err_msg = parse_config(conf)
    if err_msg is not None:
        fatal("couldn't parse '{0}': {1}".format(conf_file, err_msg))

    path_logger = PathLogger(verbose)
    for paths, rule in paths_rules:
        ok = check_files(path_logger, paths, rule)
    if not ok:
        sys.exit(1)


def fatal(s):
    print(s, file=sys.stderr)
    sys.exit(1)


def parse_config(conf):
    if conf is None:
        return (None, "is empty")

    paths_rules = []
    for i, rule in enumerate(conf):
        required = ['paths', 'comment_markers']
        for key in required:
            if key not in rule:
                return (None, "`[{0}]` doesn't contain '{1}'".format(i, key))

        paths = set()
        for j, path in enumerate(rule['paths']):
            if 'include' in path:
                if 'exclude' in path:
                    msg = "`[{0}].paths[{1}]` contains both 'include' and" \
                        " 'exclude'".format(i)
                    return (None, msg)
                incl = glob.glob(path['include'], recursive=True)
                paths.update(incl)
            elif 'exclude' in path:
                excl = glob.glob(path['exclude'], recursive=True)
                paths.difference_update(excl)
            else:
                msg = "`[{0}].paths[{1}]` doesn't contain 'include' or" \
                    " 'exclude'".format(i, j)
                return (None, msg)

        if len(paths) == 0:
            return (None, "`[{0}].paths` doesn't match any files".format(i))

        comment_markers = rule['comment_markers']

        if 'line' not in comment_markers:
            return (None, "doesn't contain 'comment_markers.line'")
        line_comment_marker = comment_markers['line']

        block_comment_marker = None
        if 'block' in comment_markers:
            block_comment_marker = comment_markers['block']

        allowed_violations = set()
        if 'allow' in rule:
            allowed_violations = set(rule['allow'])
            invalid_err_codes = allowed_violations.difference(ERR_MSGS.keys())
            if len(invalid_err_codes) != 0:
                msg = "`[{0}]` contains invalid error codes: {1}".format(
                    i,
                    "'" + "', '".join(invalid_err_codes) + "'",
                )
                return (None, msg)

        paths_rules.append((
            paths,
            (
                line_comment_marker,
                block_comment_marker,
                ErrPrinter(allowed_violations),
            ),
        ))

    return (paths_rules, None)


def check_files(path_logger, paths, rule):
    errs_found = False
    for path in paths:
        path_logger.log(path)
        with open(path) as f:
            if not check_file(path, rule, f):
                errs_found = True
    return not errs_found


def check_file(path, rule, f):
    line_comment_prefix, block_comment_prefix, err_printer = rule

    errs_found = False
    cur_block = None
    line_num = 1
    for line in f:
        if line[-1] == '\n':
            line = line[:-1]

        # We rely on external formatting tools to ensure that leading
        # whitespace is correct.
        line = line.lstrip()

        if block_comment_prefix is not None \
                and line.startswith(block_comment_prefix):
            err_code = 'block_comment'
            err_printer.print(path, line_num, err_code, ([line], 0))
            errs_found = True

        if line.startswith(line_comment_prefix):
            stripped_line = line[len(line_comment_prefix):]
            if cur_block is None:
                cur_block = (line_num, [line], [stripped_line])
            else:
                cur_block[1].append(line)
                cur_block[2].append(stripped_line)
        else:
            if code_block_has_err(err_printer, path, cur_block):
                errs_found = True
            cur_block = None

            for index in find_all(line, line_comment_prefix):
                if not is_likely_in_str(line, index):
                    err_code = 'trailing_comment'
                    preview = ([line], 0)
                    err_printer.print(path, line_num, err_code, preview)
                    break

        line_num += 1

    if code_block_has_err(err_printer, path, cur_block):
        errs_found = True

    return not errs_found


def code_block_has_err(err_printer, path, cur_block):
    """
        Output an error and return `True` if an error is found in `cur_block`.
    """
    if cur_block is None:
        return False

    block_start_line_num, block_lines, stripped_block_lines = cur_block
    err = check_comment_block(stripped_block_lines)
    if err is None:
        return False

    err_line_offset, err_code = err
    err_printer.print(
        path,
        block_start_line_num + err_line_offset,
        err_code,
        (block_lines, err_line_offset),
    )
    return True


def check_comment_block(lines):
    is_new_section = True
    prev_line = None

    for i, line in enumerate(lines):
        if len(line) == 0:
            if i == 0:
                return (i, 'block_starts_empty')
            if i == len(lines)-1:
                return (i, 'block_ends_empty')

            if not prev_line.startswith('    ') \
                    and not prev_line.endswith('.') \
                    and not prev_line.endswith(':'):
                return (i - 1, 'no_section_ending_punctuation')

            is_new_section = True
            prev_line = line
            continue

        line, ok = try_lstrip(line, ' ')
        if not ok:
            return (i, 'no_leading_space')

        if is_new_section:
            tagged = False
            for tag in ['FIXME', 'NOTE', 'TODO']:
                line, tagged = try_lstrip(line, tag)
                if tagged:
                    line, ok = try_lstrip(line, ' ')
                    if not ok:
                        return (i, 'no_leading_space_after_tag')
                    break

            if line[0].islower():
                err_code = 'starts_with_lowercase'
                if tagged:
                    err_code = 'starts_with_lowercase_after_tag'
                return (i, err_code)

        is_new_section = False
        prev_line = line

    if not prev_line.startswith('    ') and not prev_line.endswith('.'):
        return (i, 'no_ending_punctuation')

    return None


def try_lstrip(line, prefix):
    if line.startswith(prefix):
        return (line[len(prefix):], True)
    return (line, False)


class ErrPrinter:
    def __init__(self, allowed_violations):
        self._allowed_violations = allowed_violations

    def print(
        self,
        fpath,
        err_line_num,
        err_code,
        preview,
    ):
        if err_code not in self._allowed_violations:
            err_lines, err_index = preview
            print('{}:{}: ({}) {}:{}\n'.format(
                fpath,
                err_line_num,
                err_code,
                ERR_MSGS[err_code],
                render_err_lines(err_index, err_lines),
            ))


ERR_MSGS = {
    'block_comment':
        "Block comment",
    'block_starts_empty':
        "Comment blocks can't start with an empty line",
    'block_ends_empty':
        "Comment blocks can't end with an empty line",
    'no_section_ending_punctuation':
        "Sections of comment blocks must end with `.` or `:`",
    'no_leading_space':
        "Non-empty line comments must start with a space",
    'no_leading_space_after_tag':
        "Tagged comments must start with a space",
    'starts_with_lowercase':
        "Letters at the start of comment sections must be capitalised",
    'starts_with_lowercase_after_tag':
        "Letters at the start of tagged comments must be capitalised",
    'no_ending_punctuation':
        "Comment blocks must end with `.`",
    'trailing_comment':
        "Comments must be on their own line",
}


def render_err_lines(err_line_index, lines):
    s = ''
    for (i, line) in enumerate(lines):
        s += '\n{} {}'.format(
            '>' if i == err_line_index else ' ',
            line.lstrip(),
        )
    return s


def find_all(s, substr):
    """
        Return a list of indices of non-overlapping occurrences of `substr`
        within `s`.
    """
    indexs = []
    cur_index = -1
    while True:
        cur_index = s.find(substr, cur_index + 1)
        if cur_index == -1:
            break
        indexs.append(cur_index)
    return indexs


def is_likely_in_str(line, index):
    """
        Return `True` if the `index` is likely to be within a string, according
        to the handling of strings in typical programming languages. Index `0`
        is considered to be within a string.
    """
    cur_str_char = None
    escaped = False

    def in_str():
        return cur_str_char is not None

    for i, char in enumerate(line[:index]):
        if char in ['\'', '"', '`']:
            if in_str():
                if char == cur_str_char and not escaped:
                    cur_str_char = None
            else:
                cur_str_char = char

        escaped = in_str() and char == '\\' and not escaped

    return in_str()


class PathLogger:
    def __init__(self, enabled):
        self._enabled = enabled

    def log(self, path):
        if self._enabled:
            print("Checking '{}'...".format(path))


if __name__ == '__main__':
    main()
