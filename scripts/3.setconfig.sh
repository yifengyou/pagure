#!/bin/bash

set -x
cp pagure.conf /etc/httpd/conf.d/pagure.conf 
cp pagure.wsgi /usr/share/pagure/pagure.wsgi

echo "All done!"
