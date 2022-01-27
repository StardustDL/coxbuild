from pathlib import Path

from coxbuild import get_working_directory
from coxbuild.schema import depend, group, precond, run, task

from .. import projectSettings
from . import grouped, settings
from .package import hasPackages, upgradePackages

grouped = group("docs", grouped)


@grouped
@precond(lambda: not hasPackages({"Sphinx": "*"}))
@task
def restore():
    """Restore Python docs tools."""
    upgradePackages("Sphinx")


@grouped
@depend(restore)
@task
def sphinx_init(docs: Path | None = None):
    """Initialize sphinx to generate API documents."""
    run(["sphinx-quickstart"], cwd=docs or projectSettings.docs)


@grouped
@depend(restore)
@task
def sphinx_api(src: Path | None = None, docs: Path | None = None):
    """Use sphinx to generate API documents."""
    run(["sphinx-apidoc", "-o", "source", str(src or projectSettings.src)],
        cwd=docs or projectSettings.docs)


@grouped
@depend(sphinx_api)
@task
def sphinx_html(docs: Path | None = None):
    """Use sphinx to generate API documents in HTML."""
    run(["sphinx-build", "-b", "html", ".", "_build"],
        cwd=docs or projectSettings.docs)


@grouped
@depend(sphinx_html)
@task
def apidoc():
    """Generate API documents to {projectSettings.docs}/_build."""
    pass
