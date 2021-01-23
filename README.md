`comment_style`
=============

About
-----

`comment_style` is an opinionated tool that highlights issues related to comment
formatting.

Usage
-----

Run `comment_style.py` with a glob pattern for source files to check, and the
marker for line comments in the source language:

    $ python3 comment_style.py '**/*.go' '//'

The above will output any rule violations found in Go source files.

An optional marker for block comments can be provided, and the tool will
highlight any lines where that marker is found as a violation:

    $ python3 comment_style.py '**/*.go' '//' '/*'

Development
-----------

### Build environment

The build environment for the project is defined in `build.Dockerfile`.  The
build environment can be replicated locally by following the setup defined in
the Dockerfile, or Docker can be used to mount the local directory in the build
environment by running the following:

    $ bash scripts/with_build_env.sh bash

Note that the requirements for the project must be installed before doing
anything. These can be installed locally, or through the interactive Bash
session started above:

    $ pip3 install -r requirements.txt

These can also be installed in the build environment from the host:

    $ bash scripts/with_build_env.sh pip3 install -r requirements.txt

The installed packages will persist between containers for the build environment
using named volumes.

### Testing

The project can be tested locally using `make check`, or can be tested using the
Docker build environment by running the following:

    $ bash scripts/with_build_env.sh make check

Note that the environment will need to have the project requirements installed
as detailed in the previous section.

Rules/Codes
-----------

Note that tagged comments are those that start with `TODO`, `NOTE` or `FIXME`.

* `block_comment`: Block comments aren't allowed.
* `block_starts_empty`: Comment blocks can't start with an empty line.
* `block_ends_empty`: Comment blocks can't end with an empty line.
* `no_leading_space`: Non-empty line comments must start with a space.
* `no_leading_space_after_tag`: Tagged comments  must start with a space.
* `starts_with_lowercase`: Letters at the start of comments must be capitalised.
* `starts_with_lowercase_after_tag`: Letters at the start of tagged comments
  must be capitalised.
* `no_section_ending_punctuation`: Sections of comment blocks must end with `.`
  or `:`.
* `no_ending_punctuation`: Comment blocks must end with `.`.
