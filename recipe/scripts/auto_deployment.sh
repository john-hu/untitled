#!/bin/bash

# prepare workspace
WORKSPACE="/tmp/auto_silver_plate"
rm -rf $WORKSPACE
mkdir -p $WORKSPACE
cd $WORKSPACE || exit 1

# clone production branch

GIT_SSH_COMMAND="ssh -i $1 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git init
GIT_SSH_COMMAND="ssh -i $1 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git remote add origin git@github.com:john-hu/untitled.git
GIT_SSH_COMMAND="ssh -i $1 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git fetch

# check remote and local version
remote_version=$(git rev-parse origin/production)
if test -f "/opt/silver_plate/version"; then
  local_version=$(cat /opt/silver_plate/version)
else
  local_version="unknown"
fi

# check if remote and local are the same
echo "$(date) - remote version: ${remote_version}"
echo "$(date) - local version: ${local_version}"
if [ "$remote_version" == "$local_version" ]; then
  echo "$(date) - the same no need to work on it"
  exit 0
fi

echo "$(date) - start to deploy the ${remote_version}"
# check out production branch
git checkout origin/production
# build source code
echo "$(date) - build source folder ${remote_version}"
cp -r recipe "/opt/silver_plate_${remote_version}"
cp -r /opt/silver_plate/env "/opt/silver_plate_${remote_version}/env"
# create version file
echo "${remote_version}" > "/opt/silver_plate_${remote_version}/version"
if test -f "/opt/silver_plate/version"; then
  cp /opt/silver_plate/version "/opt/silver_plate_${remote_version}/old_version"
fi
cd "/opt/silver_plate_${remote_version}" || exit 1
# shellcheck disable=SC1090
source "/opt/silver_plate_${remote_version}/env/bin/activate"
# dependencies
echo "$(date) - update dependency"
pip install -r requirement.txt
# exec scrips
echo "$(date) - exec scripts"
python manage.py collectstatic
python manage.py migrate
python manage.py runscript create_schema --script-args http://localhost:8983/ recipe
chown -R silver_plate:silver_plate "/opt/silver_plate_${remote_version}"
# rebuild the links
echo "$(date) - relink"
ln -sfn "/opt/silver_plate_${remote_version}" /opt/silver_plate
# remove the old version
if test -f "/opt/silver_plate_${local_version}"; then
  echo "$(date) - remove old silver_plate_${local_version}"
  rm -rf "/opt/silver_plate_${local_version}"
fi
echo "$(date) - update finished -> restart service"
systemctl restart silver_plate
