#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install packages
poetry install --without=dev --no-root

# Convert static asset files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Run tests
python manage.py test
