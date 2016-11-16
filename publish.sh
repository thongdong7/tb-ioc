#!/usr/bin/env bash

set -e

echo Upload packages...
python setup.py bdist_wheel --universal upload -r pypi
