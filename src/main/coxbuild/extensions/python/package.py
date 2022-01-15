import shutil
from pathlib import Path
from typing import Tuple

from coxbuild.schema import depend, group, precond, run

from . import Settings, task

task = group("package", task)


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


def needRestore():
    req: Path = Settings.requirements
    if not req.exists():
        return False
    reqs = loadFromRequirements(req.read_text("utf-8").splitlines())
    return not hasPackages(reqs)


@precond(needRestore)
@task()
def restore():
    """Restore Python packages from requirements.txt."""
    run(["python", "-m", "pip", "install", "-r",
        str(Settings.requirements)], retry=3)


@precond(lambda: not hasPackages({"build": "*", "twine": "*"}))
@task()
def prebuild():
    """Restore Python package build tools."""
    upgradePackages("build", "twine")


@depend(prebuild)
@task()
def build():
    """Build Python package."""
    run(["python", "-m", "build", "-o", str(Settings.buildDist)],
        cwd=Settings.buildSrc)
    for item in Settings.buildSrc.glob("*.egg-info"):
        if not item.is_dir():
            continue
        shutil.rmtree(item)


@task()
def installBuilt():
    """Install the built package."""
    run(["python", "-m", "pip", "install",
        str(list(Settings.buildDist.glob("*.whl"))[0])])


@task()
def uninstallBuilt():
    """Uninstall the built package."""
    run(["python", "-m", "pip", "uninstall",
        str(list(Settings.buildDist.glob("*.whl"))[0]), "-y"])


@depend(build)
@task()
def deploy():
    """Upload the package to PYPI."""
    run(["python", "-m", "twine", "upload",
        "--skip-existing", "--repository", "pypi", str(Settings.buildDist) + "/*"])
