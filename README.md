`comment_style`
===============

About
-----

`comment_style` is an opinionated tool that highlights issues related to comment
formatting.

Usage
-----

Create a sample `comment_style.yaml`:

      # The set of paths to test is built up in a sequence of inclusions and
      # exclusions.
    - paths:
      - include: '**/*.go'
      - exclude: 'target/**'

      comment_markers:
        line: '//'
        # The `block` field is optional. Any lines starting with a block comment
        # marker will be flagged as an error.
        block: '/*'

      allow:
        # See the "False positives" section for more details on why it may be
        # necessary to allow `trailing_comment` violations.
      - trailing_comment

    - paths:
      - include: '**/*.py'
      - exclude: 'target/**'
      comment_markers:
        line: '#'

`comment_style.py` can then be run with the given configuration file:

    $ python3 comment_style.py comment_style.yaml

The above will output any rule violations found in the discovered Go source
files. The configuration file contains a list of rules to enable checking for
different comment markers with a single configuration file.

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
* `trailing_comment`: Comments must be on their own line.

### False positives

The check for the `trailing_comment` attempts to check whether the comment
marker is within a string to avoid false positives. However, to do this in a
language-independent way, `comment_style.py` uses a heuristic approach rather
than a syntactic one. Because of this, and because the heuristic only applies to
individual lines and not groups of lines, false positives (and false negatives)
can occur. This is especially so in the case of multi-line strings. Depending on
the scenario it may be necessary to allow violations of the `trailing_comment`
rule.

As an example, this project checks for `#` comments in shell scripts (`.sh`
files). However, `#` can naturally occur in shell scripts in the context of
`$#`. This gives a false-positive `trailing_comment` violation, so this is
allowed in the `comment_style.yaml` that this project uses.

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

    $ python3 -m pip install -r requirements.txt

These can also be installed in the build environment from the host:

    $ bash scripts/with_build_env.sh python3 -m pip install -r requirements.txt

The installed packages will persist between containers for the build environment
using named volumes.

### Testing

The project can be tested locally using `make check`, or can be tested using the
Docker build environment by running the following:

    $ bash scripts/with_build_env.sh make check

Note that the environment will need to have the project requirements installed
as detailed in the previous section.
