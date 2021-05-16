# Copyright 2021 Sean Kelleher. All rights reserved.
# Use of this source code is governed by an MIT
# licence that can be found in the LICENCE file.

# `$0` runs the installation-related integration tests for this project.

set -o errexit

python3 -m pip install .

trap 'clean_up' EXIT
clean_up() {
    python3 -m pip uninstall --yes comment_style &>/dev/null
}

comment_style comment_style.yaml

python3 -m pip uninstall --yes comment_style

comment_style comment_style.yaml \
    || test "$?" -ne 1

echo ok
