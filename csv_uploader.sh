#!/bin/bash
. /home/bemoss/BEMOSS_Plus/env/bin/activate
python /home/bemoss/BEMOSS_Plus/bemoss_lib/databases/daily_csv_output.py


sleep 5

folder="$(date --date yesterday '+%Y%m%d')"
cd /home/bemoss/BEMOSS_DATA/PGCOUNTY/
s3cmd sync ./ s3://hhb6420
