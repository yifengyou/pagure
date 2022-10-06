# -*- coding: utf-8 -*-

"""
 (c) 2018-2019 - Copyright Red Hat Inc

 Authors:
   Clement Verna <cverna@tutanota.com>
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""

from __future__ import unicode_literals, absolute_import

import flask
from pagure.flask_app import admin_session_timedout
from functools import wraps


def has_issue_tracker(function):
    """
    Decorator that checks if the current pagure project has the
    issue tracker active
    If not active returns a 404 page
    """

    @wraps(function)
    def check_issue_tracker(*args, **kwargs):
        repo = flask.g.repo
        if not flask.g.issues_enabled or not repo.settings.get(
            "issue_tracker", True
        ):
            flask.abort(
                404, description="No issue tracker found for this project"
            )
        # forbid all POST requests if the issue tracker is made read-only
        if flask.request.method == "POST" and repo.settings.get(
            "issue_tracker_read_only", False
        ):
            flask.abort(
                401,
                description="The issue tracker for this project is read-only",
            )
        return function(*args, **kwargs)

    return check_issue_tracker


def has_pr_enabled(function):
    """
    Decorator that checks if the current pagure project has the
    issue tracker active or has PRs function active
    If not active returns a 404 page
    """

    @wraps(function)
    def check_trackers(*args, **kwargs):
        repo = flask.g.repo
        if not repo.settings.get("pull_requests", True):
            flask.abort(
                404,
                description="Pull Requests are not enabled on this project",
            )

        return function(*args, **kwargs)

    return check_trackers


def has_issue_or_pr_enabled(function):
    """
    Decorator that checks if the current pagure project has either their
    issue tracker or their PR active. If both of them are disabled, it
    returns a 404 page.
    """

    @wraps(function)
    def check_issue_pr_trackers(*args, **kwargs):
        repo = flask.g.repo
        issue_enabled = flask.g.issues_enabled
        issue_ro = repo.settings.get("issue_tracker_read_only", False)
        pr_enabled = repo.settings.get("pull_requests", True)
        if not issue_enabled and not pr_enabled:
            flask.abort(
                404,
                description="Issue tracker and Pull-Request disabled for "
                "this project",
            )
        elif flask.request.method == "POST" and not pr_enabled and issue_ro:
            flask.abort(
                401,
                description="The issue tracker for this project is read-only",
            )
        return function(*args, **kwargs)

    return check_issue_pr_trackers


def is_repo_admin(function):
    """
    Decorator that checks if the current user is the admin of
    the project.
    If not active returns a 403 page
    """

    @wraps(function)
    def check_repo_admin(*args, **kwargs):
        if not flask.g.repo_admin:
            flask.abort(
                403,
                description="You are not allowed to change the "
                "settings for this project",
            )
        return function(*args, **kwargs)

    return check_repo_admin


def is_admin_sess_timedout(function):
    """
    Decorator that checks if the admin session has timeout.
    If not true redirect to the login page
    """

    @wraps(function)
    def check_session_timeout(*args, **kwargs):
        if admin_session_timedout():
            if flask.request.method == "POST":
                flask.flash("Action canceled, try it again", "error")
            return flask.redirect(
                flask.url_for("auth_login", next=flask.request.url)
            )
        return function(*args, **kwargs)

    return check_session_timeout
