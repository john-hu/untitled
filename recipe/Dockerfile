FROM python:3.9

# update and upgrade the OS
RUN apt-get update && apt-get upgrade -y
# install nginx for serving static content
RUN apt-get install nginx -y && apt-get clean -y

ENV HOME_DIR=/opt/recipe
# gunicorn related configs
ENV SERVER_IDLE_TIMEOUT=120
ENV SERVER_WORKERS=3
ENV CONNECTION_IDLE_TIMEOUT=90
ENV PID_FILE=$HOME_DIR/pid
ENV DEBUG=no
ENV CUTTING_BOARD_URL=http://host.docker.internal:8983/solr/recipe
ENV PEELER_USERNAME=peeler
ENV PEELER_PASSWORD=123456
# port for silver plate
EXPOSE 8001

WORKDIR $HOME_DIR
# copy server source files
COPY ./requirement.txt $HOME_DIR/requirement.txt
COPY ./cutting_board $HOME_DIR/cutting_board
COPY ./recipe $HOME_DIR/recipe
COPY ./silver_plate $HOME_DIR/silver_plate
COPY ./manage.py $HOME_DIR/manage.py
COPY ./server_settings/nginx.conf /etc/nginx/nginx.conf
COPY ./docker.sh $HOME_DIR/docker.sh
RUN chmod +x $HOME_DIR/docker.sh
# install 3rd dependencies
RUN pip3 install --prefer-binary -r $HOME_DIR/requirement.txt
# collect static files for django
RUN python manage.py collectstatic
# start the server
# At common cases, we should run the server in another user instead of root.
# But we need it to run the nginx for serving static files.
CMD ["./docker.sh"]
