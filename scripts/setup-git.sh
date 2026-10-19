#!/usr/bin/env bash

pip install nb-clean nbdime pre-commit
nbdime config-git --enable
pre-commit install
git config --local include.path ../repo-gitconfig

