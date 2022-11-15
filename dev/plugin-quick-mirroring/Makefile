default:
	@echo "default    show help"
	@echo "run        run python scripts in docker"
	@echo "install    install python scripts in docker"
	@echo "check      check env whether in docker"

run: check
	PAGURE_CONFIG=/etc/pagure/pagure.cfg python3 quick_mirroring.py --debug

install: check
	cp quick_mirroring.py /usr/share/pagure/quick_mirroring.py
	cp pagure_quick_mirroring.service /usr/lib/systemd/system/pagure_quick_mirroring.service -a
	cp pagure_quick_mirroring.timer /usr/lib/systemd/system/pagure_quick_mirroring.timer -a
	systemctl daemon-reload
	systemctl enable --now pagure_quick_mirroring.service pagure_quick_mirroring.timer

check:
	@[ ! -e /.dockerenv ] && echo "Fatal error! not in docker env" && exit 1 || true

status:
	systemctl status --no-pager pagure_quick_mirroring.service pagure_quick_mirroring.timer
	ps aux|grep -E 'src-openeuler|git push local' || true
	echo "total:"`ls -d /home/git/repositories/src-openeuler/*.git |wc -l` || true
	cd  /home/git/repositories/src-openeuler/ && echo "left:"`find ./ -name heads -empty |wc -l`
	cd  /home/git/repositories/src-openeuler/ && find ./ -name heads -empty 

stop:
	systemctl stop pagure_quick_mirroring.service pagure_quick_mirroring.timer

restart:
	systemctl restart pagure_quick_mirroring.service pagure_quick_mirroring.timer

start:
	systemctl start pagure_quick_mirroring.service pagure_quick_mirroring.timer

watch:
	journalctl -xe -f -u pagure_quick_mirroring
