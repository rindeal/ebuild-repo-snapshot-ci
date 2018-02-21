#!/bin/bash

set -e
set -u
set -v

# Usage: fold_start <TAG> <COMMENT>
#
# These statements can be nested and must be in pair with `fold_end()`.
fold_start() {
  echo -e "travis_fold:start:${1}\033[33;1m${2}\033[0m"
}

# Usage: fold_end <TAG>
fold_end() {
  echo -e "\ntravis_fold:end:${1}\r"
}

cd /repo

time emerge --sync
time emerge -1 --jobs=4 dev-python/git-python

fold_start "foo.py" ""
time python3 ./foo.py --c ./foo.config --o /public/repo-ci
fold_end "foo.py"
