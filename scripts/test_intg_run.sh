# Copyright 2021 Sean Kelleher. All rights reserved.
# Use of this source code is governed by an MIT
# licence that can be found in the LICENCE file.

# `$0 [test-name]` runs the run-related integration tests for this project, or
# just the integration test called `test-name` if the optional argument is
# provided.

set -o errexit

if [ $# -gt 1 ] ; then
    echo "usage: $0 [test-name]" >&2
    exit 1
fi
test_name="$1"

for conf in tests/*.yaml ; do
    cur_test_name=$(basename "$conf" | sed 's/\..*//')
    if [ ! -z "$test_name" ] && [ "$cur_test_name" != "$test_name" ] ; then
        continue
    fi

    options=
    if [ "$cur_test_name" = "verbose" ] ; then
        options='--verbose'
    fi

    echo -n "$cur_test_name..."
    python3 comment_style.py \
        "tests/$cur_test_name.yaml" \
        $options \
        &> "target/tests/$cur_test_name.act.txt" \
        || true
    diff \
        --unified \
        "tests/$cur_test_name.exp.txt" \
        "target/tests/$cur_test_name.act.txt"
    echo " ok"
done
