#!/bin/bash

set -x

python /usr/share/pagure/pagure_createdb.py -c /etc/pagure/pagure.cfg -i /etc/pagure/alembic.ini

echo "All done!"
