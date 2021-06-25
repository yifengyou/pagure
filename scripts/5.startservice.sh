#!/bin/bash

set -x

systemctl daemon-reload

systemctl status pagure_worker.service 
systemctl status pagure_gitolite_worker.service
echo "========================================="
systemctl enable --now pagure_worker.service pagure_gitolite_worker.service
sleep 3
echo "========================================="
systemctl status pagure_worker.service 
systemctl status pagure_gitolite_worker.service



echo "All done!"
