# Copyright 2021 Sean Kelleher. All rights reserved.
# Use of this source code is governed by an MIT
# licence that can be found in the LICENCE file.

# `$0 <config-yaml>` outputs issues found in comment blocks specified in
# `config-yaml`. Only the first issue encountered in each comment block is
# output.

import glob
import sys
import yaml


def main():
    if len(sys.argv) != 2:
        print("usage: {0} <config-yaml>".format(sys.argv[0]))
        sys.exit(1)

    conf_file = sys.argv[1]
    with open(conf_file) as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    parsed_conf, err_msg = parse_config(conf)
    if err_msg is not None:
        print("couldn't parse '{0}': {1}".format(conf_file, err_msg))
        sys.exit(1)

    paths, line_comment_prefix, block_comment_prefix = parsed_conf
    ok = check_files(paths, line_comment_prefix, block_comment_prefix)
    if not ok:
        sys.exit(1)


def parse_config(conf):
    if conf is None:
        return (None, "is empty")

    required = ['paths', 'comment_markers']
    for key in required:
        if key not in conf:
            return (None, "doesn't contain '{0}'".format(key))

    paths = set()
    for i, path in enumerate(conf['paths']):
        if 'include' in path:
            if 'exclude' in path:
                msg = "'paths'[{0}] contains both 'include' and 'exclude'" \
                    .format(i)
                return (None, msg)
            incl = glob.glob(path['include'], recursive=True)
            paths.update(incl)
        elif 'exclude' in path:
            excl = glob.glob(path['exclude'], recursive=True)
            paths.symmetric_difference_update(excl)
        else:
            msg = "'paths'[{0}] doesn't contain 'include' or 'exclude'" \
                .format(i)
            return (None, msg)

    comment_markers = conf['comment_markers']

    if 'line' not in comment_markers:
        return (None, "doesn't contain 'comment_markers.line'")
    line_comment_marker = comment_markers['line']

    block_comment_marker = None
    if 'block' in comment_markers:
        block_comment_marker = comment_markers['block']

    parsed_conf = (paths, line_comment_marker, block_comment_marker)
    return (parsed_conf, None)


def check_files(paths, line_comment_prefix, block_comment_prefix):
    errs_found = False

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
