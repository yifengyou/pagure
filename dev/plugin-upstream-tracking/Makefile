default:
	@echo "default    show help"
	@echo "run        run python scripts in docker"
	@echo "install    install python scripts in docker"
	@echo "check      check env whether in docker"

run: check
	PAGURE_CONFIG=/etc/pagure/pagure.cfg python3 upstream_tracking.py --debug

install: check
	cp upstream_tracking.py /usr/share/pagure/upstream_tracking.py
	cp pagure_upstream_tracking.service /usr/lib/systemd/system/pagure_upstream_tracking.service -a
	cp pagure_upstream_tracking.timer /usr/lib/systemd/system/pagure_upstream_tracking.timer -a
	systemctl daemon-reload
	systemctl enable --now pagure_upstream_tracking.service pagure_upstream_tracking.timer

check:
	@[ ! -e /.dockerenv ] && echo "Fatal error! not in docker env" && exit 1 || true

status:
	systemctl status --no-pager pagure_upstream_tracking.service pagure_upstream_tracking.timer

stop:
	systemctl stop pagure_upstream_tracking.service pagure_upstream_tracking.timer

restart:
	systemctl restart pagure_upstream_tracking.service pagure_upstream_tracking.timer

start:
	systemctl start pagure_upstream_tracking.service pagure_upstream_tracking.timer

watch:
	journalctl -xe -f -u pagure_upstream_tracking
