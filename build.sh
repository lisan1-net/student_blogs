#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install packages
poetry install

# Apply database migrations
python manage.py migrate
