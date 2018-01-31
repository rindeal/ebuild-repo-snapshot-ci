#!/bin/bash

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

export LANG=en_US
export LANGUAGE=${LANG}
export LC_ALL=${LANG}.UTF-8
env-update

cd /repo

fold_start "equo.install"
equo install --verbose --multifetch 4 sys-apps/portage
fold_end "equo.install"

fold_start "foo.py"
./foo.py --c ./foo.config --o /tmp/repo-ci
fold_end "foo.py"
