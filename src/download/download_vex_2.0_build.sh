#!/bin/sh

filepath=$(cd "$(dirname "$0")"; pwd)
echo $filepath

user_name=yanyang.xie
password=123456

python $filepath/download_sona_build.py -u ${user_name} -p ${password} -n vex -v 2.0.0-SNAPSHOT -e release.zip
python $filepath/download_sona_build.py -u ${user_name} -p ${password} -n vex-frontend -v 2.0.0-SNAPSHOT -e release.zip