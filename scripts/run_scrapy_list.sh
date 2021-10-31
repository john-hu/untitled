#!/bin/bash

echo "[$(date '+%F %X')] execute peeler - $1 list"
source /home/pi/git/untitled/env/bin/activate
cd /home/pi/git/untitled/
python -u -m peeler.$1 list 2>&1

