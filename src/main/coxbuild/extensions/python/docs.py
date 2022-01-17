from coxbuild import get_working_directory
from coxbuild.schema import depend, group, precond, run

from . import settings, task
from .package import hasPackages, upgradePackages

task = group("docs", task)


@precond(lambda: not hasPackages({"Sphinx": "*"}))
@task()
def restore():
    """Restore Python docs tools."""
    upgradePackages("Sphinx")


@depend(restore)
@task()
def sphinx_api():
    """Use sphinx to generate API documents."""
    run(["sphinx-apidoc", "-o", "source", str(settings.src)], cwd=settings.apidocs)


@depend(sphinx_api)
@task()
def sphinx_html():
    """Use sphinx to generate API documents in HTML."""
    run(["sphinx-build", "-b", "html", ".", "_build"], cwd=settings.apidocs)


@depend(sphinx_html)
@task()
def apidoc():
    """Generate API documents to {settings.apidocs}/_build."""
    pass
