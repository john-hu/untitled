#!/bin/bash

source env/bin/activate
echo "$(date): start gunicorn + django server"
exec gunicorn\
     --workers 3\
     --worker-class gevent\
     --timeout 90\
     --keep-alive 120\
     recipe.wsgi:application
