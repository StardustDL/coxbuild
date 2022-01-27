import shutil
from pathlib import Path
from typing import Tuple

from coxbuild.schema import depend, group, precond, run, task

from .. import projectSettings
from . import grouped, settings

grouped = group("package", grouped)


def loadFromRequirements(lines: list[str]) -> dict[str, str]:
    results: dict[str, str] = {}
    for line in lines:
        sl = line.split("==")
        if len(sl) != 2:
            continue
        k, v = sl
        results[k] = v
    return results


def installedPackages() -> dict[str, str]:
    output = run(["python", "-m", "pip", "freeze"], pipe=True).stdout
    return loadFromRequirements(output.splitlines())


def hasPackages(packages: dict[str, str]):
    installed = installedPackages()
    for p, v in packages.items():
        if p not in installed or (v != "*" and installed[p] != v):
            return False
    return True


def upgradePackages(*packages: str):
    run(["python", "-m", "pip", "install", "--upgrade", *packages], retry=3)


@grouped
@task
def restore(requirements: Path | None = None):
    """Restore Python packages from requirements.txt."""
    run(["python", "-m", "pip", "install", "-r",
        str(requirements or settings.requirements)], retry=3)


@restore.precond
def needRestore():
    req: Path = settings.requirements
    if not req.exists():
        return False
    reqs = loadFromRequirements(req.read_text("utf-8").splitlines())
    return not hasPackages(reqs)


@grouped
@precond(lambda: not hasPackages({"build": "*", "twine": "*"}))
@task
def prebuild():
    """Restore Python package build tools."""
    upgradePackages("build", "twine")


@grouped
@depend(prebuild)
@task
def build(src: Path | None = None, dist: Path | None = None):
    """Build Python package."""
    src = src or projectSettings.src
    run(["python", "-m", "build", "-o", str(dist or projectSettings.package)],
        cwd=src)
    for item in src.glob("*.egg-info"):
        if not item.is_dir():
            continue
        shutil.rmtree(item)


@grouped
@task
def installBuilt(dist: Path | None = None):
    """Install the built package."""
    run(["python", "-m", "pip", "install",
        str(list((dist or projectSettings.package).glob("*.whl"))[0])])


@grouped
@task
def uninstallBuilt(dist: Path | None = None):
    """Uninstall the built package."""
    run(["python", "-m", "pip", "uninstall",
        str(list((dist or projectSettings.package).glob("*.whl"))[0]), "-y"])


@grouped
@depend(build)
@task
def deploy(dist: Path | None = None):
    """Upload the package to PYPI."""
    run(["python", "-m", "twine", "upload",
        "--skip-existing", "--repository", "pypi", str(dist or projectSettings.package) + "/*"])
