#!/bin/bash
while getopts p:e:u:d: flag
do
  case "${flag}" in
    p) PEELER=${OPTARG};;
    e) ENDPOINT=${OPTARG};;
    u) USER=${OPTARG};;
    d) PASSWD=${OPTARG};;
  esac
done

echo "peeler=$PEELER"
echo "endpoint=$ENDPOINT"
echo "username=$USER"

for file in peeler_output/${PEELER}/*.json; do
  echo "$(date) - upload the whole file ${file} to ${ENDPOINT}"
  python -m peeler.utils.uploader --endpoint ${ENDPOINT} --username ${USER} --password ${PASSWD} --mode push_all $file
done
