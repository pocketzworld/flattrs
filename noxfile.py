from __future__ import annotations

import os

import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = True


def _cov(session: nox.Session) -> None:
    session.run("coverage", "run", "-m", "pytest", *session.posargs)

    if os.environ.get("CI") != "true":
        session.notify("coverage_report")


@nox.session(python=["3.9", "3.11"], tags=["tests"])
def tests_cov(session: nox.Session) -> None:
    session.install(".[dev]")

    _cov(session)


@nox.session(python=["3.9", "3.10", "3.11"], tags=["tests"])
def tests(session: nox.Session) -> None:
    session.install(".[dev]")

    session.run("pytest", *session.posargs)


@nox.session
def coverage_report(session: nox.Session) -> None:
    session.install("coverage[toml]")

    session.run("coverage", "combine")
    session.run("coverage", "report")
