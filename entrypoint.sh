#!/bin/bash

python manage.py migrate --no-input
python manage.py collectstatic --no-input

gunicorn issue_tracker.wsgi:application --bind 0.0.0.0:8000

