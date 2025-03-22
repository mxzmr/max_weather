#!/bin/bash

# Number of workers = (2 * CPU cores) + 1
WORKERS=3

# Start Gunicorn
gunicorn --workers $WORKERS \
         --bind 0.0.0.0:8080 \
         --access-logfile - \
         --error-logfile - \
         --reload \
         wsgi:app
