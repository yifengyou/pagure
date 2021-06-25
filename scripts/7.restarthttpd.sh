#!/bin/bash

set -x

systemctl restart httpd

systemctl status httpd
echo "All done!"
