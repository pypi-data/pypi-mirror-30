# pyshuff

An inexact clone of GNU shuf. Free, implemented in Python.

### Install

### Usage

Same as shuf, but the script is invoked with pyshuf. Read the [GNU
manual](https://www.gnu.org/software/coreutils/manual/html_node/shuf-invocation.html)
for shuf for more details. I haven't used shuf -- I wrote this because it
didn't come standard on MacOS.

### Implemented

    --e, --echo
    -i, --input-range
    -n, --head-count

### Not implemented

    -o, --output-file
    --random-source
    -r, --repeat
    -z, --zero-terminated

### Added

    --input-file	specify an input file to read from