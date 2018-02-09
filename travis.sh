#!/bin/bash

set -e

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

fold_start "entropy.license.accept"
rsync --no-motd "rsync://rsync.gentoo.org/gentoo-portage/licenses/*" | awk '{print $5}' >> /etc/entropy/packages/license.accept
fold_end "entropy.license.accept"

fold_start "equo.mirrorsort"
time equo repo mirrorsort sabayonlinux.org
echo
echo "/etc/entropy/repositories.conf.d/entropy_sabayonlinux.org:"
echo
cat /etc/entropy/repositories.conf.d/entropy_sabayonlinux.org
echo
echo "/etc/entropy/client.conf:"
echo
cat /etc/entropy/client.conf
fold_end "equo.mirrorsort"

fold_start "equo.install"
time equo install --verbose --multifetch 4 sys-apps/portage dev-vcs/git dev-python/setuptools app-text/tree
fold_end "equo.install"

fold_start "entropy.tree"
tree /etc/entropy
fold_end "entropy.tree"

fold_start "equo.install"
time emerge --sync
time emerge --ask=n dev-python/git-python
fold_end "equo.install"

fold_start "foo.py"
time python3 ./foo.py --c ./foo.config --o /tmp/repo-ci
fold_end "foo.py"
