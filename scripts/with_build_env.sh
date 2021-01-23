# Copyright 2021 Sean Kelleher. All rights reserved.
# Use of this source code is governed by an MIT
# licence that can be found in the LICENCE file.

# `$0` runs a command in the build environment.

set -o errexit

proj='comment_style'
build_img="$proj.build"

bash scripts/docker_rbuild.sh \
    "$build_img" \
    'latest' \
    --file='build.Dockerfile' \
    .

cache_vol="$proj.cache"
cache_dir="/cache"
cache_mount="type=volume,src=$cache_vol,dst=$cache_dir"
docker run \
    --rm \
    --mount="$cache_mount" \
    "$build_img:latest" \
    chmod 0777 "$cache_dir"

echo "$@"

# We set the `HOME` environment directory to our `$cache_dir` as this is where
# Python installs cache files, notably in `$HOME/.cache` and `$HOME/.local`.
docker run \
    --interactive \
    --tty \
    --rm \
    --mount="$cache_mount" \
    --env="HOME=$cache_dir" \
    --user="$(id -u):$(id -g)" \
    --mount="type=bind,src=$(pwd),dst=/app" \
    --workdir='/app' \
    "$build_img:latest" \
    bash \
        -c \
        "PATH=$cache_dir/.local/bin:$PATH $*"
