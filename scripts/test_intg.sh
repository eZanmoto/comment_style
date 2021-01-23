# Copyright 2021 Sean Kelleher. All rights reserved.
# Use of this source code is governed by an MIT
# licence that can be found in the LICENCE file.

# `$0` runs the integration tests for this project.

set -o errexit

for conf in tests/*.exp.txt ; do
    src_lang=$(basename "$conf" | sed 's/\..*//')
    case "$src_lang" in
        go)
            python3 comment_style.py \
                "tests/test.$src_lang" \
                '//' \
                '/*' \
                > "target/tests/$src_lang.act.txt" \
                || true
            ;;
    esac
    diff \
        "target/tests/$src_lang.act.txt" \
        "tests/$src_lang.exp.txt"
done
