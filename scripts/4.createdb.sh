#!/bin/bash

set -x

if [ -f /var/tmp/pagure_dev.sqlite ];then
	ls -alh /var/tmp/pagure_dev.sqlite
fi
python3 /usr/share/pagure/pagure_createdb.py -c /etc/pagure/pagure.cfg -i /etc/pagure/alembic.ini

if [ $? -eq 0 ];then
	echo "All ok"
else
	echo "Failed!"
fi

ls -alh /var/tmp/pagure_dev.sqlite

