#!/bin/bash

echo "make sure alembic.ini script_location value config right! "
cat alembic.ini |grep script_location
sleep 3
python createdb.py --initial alembic.ini
