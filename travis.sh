#!/bin/bash

equo install --verbose --multifetch 4 sys-apps/portage app-portage/repoman
./foo.py --c foo.config --o /tmp/repo-ci
