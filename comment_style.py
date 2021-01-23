# Copyright 2021 Sean Kelleher. All rights reserved.
# Use of this source code is governed by an MIT
# licence that can be found in the LICENCE file.

# `$0 <glob-pattern> <line-comment-prefix> [multi-line-prefix]` outputs issues
# found in comment blocks prefixed by `line-comment-prefix`, discovered in
# files matching `glob-pattern`. Only the first issue encountered in each
# comment block is output.
#
# If `multi-line-prefix` is provided then any lines starting with the given
# prefix will be flagged as an error.

import glob
import sys


def main():
    if len(sys.argv) < 3:
        msg = "usage: {0} <glob-pattern> <line-comment-prefix>" \
            + " [block-comment-prefix]".format(sys.argv[0])
        print(msg)
        sys.exit(1)

    [glob_pattern, line_comment_prefix] = sys.argv[1:3]
    block_comment_prefix = None
    if len(sys.argv) > 3:
        block_comment_prefix = sys.argv[3]

    ok = check_files(glob_pattern, line_comment_prefix, block_comment_prefix)
    if not ok:
        sys.exit(1)


def check_files(glob_pattern, line_comment_prefix, block_comment_prefix):
    errs_found = False

    paths = glob.glob(glob_pattern, recursive=True)
    for path in paths:
        with open(path) as f:
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
                    print(render_err(path, line_num, err_code, [line], 0))
                    errs_found = True

                if line.startswith(line_comment_prefix):
                    stripped_line = line[len(line_comment_prefix):]
                    if cur_block is None:
                        cur_block = (line_num, [line], [stripped_line])
                    else:
                        cur_block[1].append(line)
                        cur_block[2].append(stripped_line)
                else:
                    errs_found = \
                        maybe_check_code_block(path, cur_block) or errs_found
                    cur_block = None

                line_num += 1

            errs_found = maybe_check_code_block(path, cur_block) or errs_found
            cur_block = None

    return not errs_found


def maybe_check_code_block(path, cur_block):
    """
        Output an error and return `True` if an error is found in `cur_block`.
    """
    if cur_block is not None:
        block_start_line_num, block_lines, stripped_block_lines = cur_block
        err = check_comment_block(stripped_block_lines)
        if err is not None:
            err_line_offset, err_code = err
            print(render_err(
                path,
                block_start_line_num + err_line_offset,
                err_code,
                block_lines,
                err_line_offset,
            ))
            return True
    return False


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


def render_err(fpath, err_line_num, err_code, preview_lines, err_line_offset):
    return '{}:{}: ({}) {}:{}\n'.format(
        fpath,
        err_line_num,
        err_code,
        ERR_MSGS[err_code],
        render_err_lines(err_line_offset, preview_lines),
    )


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
}


def render_err_lines(err_line_index, lines):
    s = ''
    for (i, line) in enumerate(lines):
        s += '\n{} {}'.format(
            '>' if i == err_line_index else ' ',
            line.lstrip(),
        )
    return s


if __name__ == '__main__':
    main()
