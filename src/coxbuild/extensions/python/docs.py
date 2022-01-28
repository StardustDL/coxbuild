from pathlib import Path

from coxbuild import get_working_directory
from coxbuild.schema import depend, group, precond, run, task

from .. import ProjectSettings, withProject
from . import grouped
from .package import hasPackages, upgradePackages

subgrouped = group("docs")


@grouped
@subgrouped
@precond(lambda: not hasPackages({"Sphinx": "*"}))
@task
def restore():
    """Restore Python docs tools."""
    upgradePackages("Sphinx")


@grouped
@subgrouped
@withProject
@depend(restore)
@task
def sphinx_init(docs: Path | None = None, *, project: ProjectSettings):
    """Initialize sphinx to generate API documents."""
    run(["sphinx-quickstart"], cwd=docs or project.docs)


@grouped
@subgrouped
@withProject
@depend(restore)
@task
def sphinx_api(src: Path | None = None, docs: Path | None = None, *, project: ProjectSettings):
    """Use sphinx to generate API documents."""
    run(["sphinx-apidoc", "-o", "source", str(src or project.src)],
        cwd=docs or project.docs)


@grouped
@subgrouped
@depend(sphinx_api)
@withProject
@task
def sphinx_html(docs: Path | None = None, *, project: ProjectSettings):
    """Use sphinx to generate API documents in HTML."""
    run(["sphinx-build", "-b", "html", ".", "_build"],
        cwd=docs or project.docs)


@grouped
@subgrouped
@depend(sphinx_html)
@task
def apidoc():
    """Generate API documents to {projectSettings.docs}/_build."""
    pass
