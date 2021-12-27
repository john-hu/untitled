#!/bin/bash

source /opt/env39/bin/activate
source /opt/.env
echo "$(date): start gunicorn + django server"
exec gunicorn\
     --workers 3\
     --worker-class gevent\
     --timeout 90\
     --keep-alive 120\
     --log-config server_settings/image/gunicorn_logging.config\
     recipe.wsgi:application

