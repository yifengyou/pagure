#!/bin/bash

if [ -f /var/tmp/pagure_dev.sqlite ];then
	rm -rf /var/tmp/pagure_dev.sqlite
	echo "clean sqlite:////var/tmp/pagure_dev.sqlite"
fi

if [ -d lcl ];then
	rm -rf lcl
	echo "remove lcl dir"
	mkdir -p lcl/{repos,remotes,attachments,releases}
	echo "mkdir -p lcl/{repos,remotes,attachments,releases}"
fi

if [ -d /root/learn-pagure/repos ];then
	rm -rf /root/learn-pagure/repos
	echo "remove /root/learn-pagure/repos dir"
	mkdir -p /root/learn-pagure/repos
	echo "mkdir -p /root/learn-pagure/repos"
fi

./2.createdb.sh
