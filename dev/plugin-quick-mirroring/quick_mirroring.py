#!/usr/bin/env python

from __future__ import print_function, absolute_import
import os
import argparse
import multiprocessing
import random, time, fcntl
from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError

import pagure.config
import pagure.lib.model as model
import pagure.lib.model_base
import pagure.lib.notify
import pagure.lib.query

if "PAGURE_CONFIG" not in os.environ and os.path.exists(
        "/etc/pagure/pagure.cfg"
):
    print("Using configuration file `/etc/pagure/pagure.cfg`")
    os.environ["PAGURE_CONFIG"] = "/etc/pagure/pagure.cfg"

_config = pagure.config.reload_config()

import random, time


def check_instance_running(lockfile):
    lock_file_pointer = os.open(lockfile, os.O_CREAT | os.O_WRONLY)
    try:
        fcntl.lockf(lock_file_pointer, fcntl.LOCK_EX | fcntl.LOCK_NB)
        already_running = False
    except IOError:
        already_running = True
    return already_running


def do_main(project, debug):
    session = pagure.lib.model_base.create_session(_config["DB_URL"])
    if debug:
        print("Mirrorring %s (%s)" % (project.fullname, project.path))
    try:
        pagure.lib.git.mirror_pull_project(session, project, debug=debug)
    except Exception as err:
        print("ERROR: %s" % err)
    if debug:
        session.remove()
        print("session removed!")


def main(check=False, debug=True):
    lockfile = f'/tmp/mirror.lock'
    data = check_instance_running(lockfile)
    if data:
        raise Exception(f"App pagure_mirror_project_in already running")

    """ The function pulls in all the changes from upstream"""
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    session = pagure.lib.model_base.create_session(_config["DB_URL"])
    projects = (
        session.query(model.Project)
            .filter(model.Project.mirrored_from != None)
            .all()
    )
    session.remove()
    for project in projects[::-1]:
        if project.fullname != "src-openeuler/java-1.8.0-openjdk":
            continue

        if debug:
            print("Mirrorring %s" % project.fullname)
        pool.apply_async(do_main, args=(project, debug,))
    pool.close()
    pool.join()

    if debug:
        print("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to send email before the api token expires"
    )
    parser.add_argument(
        "--check",
        dest="check",
        action="store_true",
        default=False,
        help="Print the some output but does not send any email",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Print the debugging output",
    )
    args = parser.parse_args()
    main(debug=args.debug)
