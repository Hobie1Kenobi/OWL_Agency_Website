#!/usr/bin/env bash
# Render build script — upgrade pip, install deps with pre-built wheels
set -o errexit
pip install --upgrade pip
pip install -r requirements.txt
