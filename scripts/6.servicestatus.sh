#!/bin/bash

set -x

systemctl status pagure_worker.service 
systemctl status pagure_gitolite_worker.service

echo "All done!"
