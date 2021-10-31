#!/bin/bash

echo "[$(date '+%F %X')] execute peeler - $1 result"
source /home/pi/git/untitled/env/bin/activate
cd /home/pi/git/untitled/
python -u -m peeler.$1 --count 60 result 2>&1

