# Copyright 2021 Sean Kelleher. All rights reserved.
# Use of this source code is governed by an MIT
# licence that can be found in the LICENCE file.

# `$0` runs the integration tests for this project.

set -o errexit

for conf in tests/*.yaml ; do
    test_name=$(basename "$conf" | sed 's/\..*//')
    echo -n "$test_name..."
    python3 comment_style.py \
        "tests/$test_name.yaml" \
        &> "target/tests/$test_name.act.txt" \
        || true
    diff \
        --unified \
        "tests/$test_name.exp.txt" \
        "target/tests/$test_name.act.txt"
    echo " ok"
done
