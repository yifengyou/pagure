#!/bin/bash


mkdir -p /var/www/releases
useradd git -s /sbin/nologin || true
chown git:git /var/www/releases

mkdir -p /srv/git/repositories/{docs,forks,tickets,requests,remotes}
