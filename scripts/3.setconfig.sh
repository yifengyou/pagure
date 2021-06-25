#!/bin/bash

set -x

cp pagure.conf /etc/httpd/conf.d/pagure.conf 
cp pagure.wsgi /usr/share/pagure/pagure.wsgi
cp doc_pagure.wsgi /usr/share/pagure/doc_pagure.wsgi
cp pagure.cfg /etc/pagure/pagure.cfg

echo "All done!"
