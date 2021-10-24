#!/bin/sh
nginx
echo "$(date): start gunicorn + django server"
exec gunicorn\
     --pid ${PID_FILE}\
     --bind unix:/opt/recipe/gunicorn.sock\
     --workers ${SERVER_WORKERS}\
     --worker-class gevent\
     --timeout ${SERVER_IDLE_TIMEOUT}\
     --keep-alive ${CONNECTION_IDLE_TIMEOUT}\
     recipe.wsgi:application
