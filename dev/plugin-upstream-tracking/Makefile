default:
	@echo "default    show help"
	@echo "run        run python scripts in docker"
	@echo "install    install python scripts in docker"
	@echo "check      check env whether in docker"

run: check
	PAGURE_CONFIG=/etc/pagure/pagure.cfg python3 upstream_tracking.py --debug

install: check
	cp pagure_upstream_tracking.service /usr/lib/systemd/system/pagure_upstream_tracking.service -a
	cp pagure_upstream_tracking.timer /usr/lib/systemd/system/pagure_upstream_tracking.timer -a
	systemctl daemon-reload

check:
	@[ ! -e /.dockerenv ] && echo "Fatal error! not in docker env" && exit 1 || true
