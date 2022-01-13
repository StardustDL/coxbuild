from pathlib import Path
from typing import Tuple
from . import task, mconfig
from coxbuild.schema import depend, precond, run, group

task = group("package", task)


def loadFromRequirements(lines: list[str]) -> dict[str, str]:
    results: dict[str, str] = {}
    for line in lines:
        k, v = line.split("==")
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


def needRestore():
    req: Path = mconfig["requirements"]
    if not req.exists():
        return False
    reqs = loadFromRequirements(req.read_text("utf-8").splitlines())
    return not hasPackages(reqs)


@precond(needRestore)
@task()
def restore():
    run(["python", "-m", "pip", "install", "-r",
        str(mconfig["requirements"])], retry=3)


@precond(lambda: not hasPackages({"build": "*", "twine": "*"}))
@task()
def prebuild():
    run(["python", "-m", "pip", "install", "--upgrade", "build", "twine"], retry=3)


@depend(prebuild)
@task()
def build():
    run(["python", "-m", "build", "-o", str(mconfig["buildDist"])],
        cwd=mconfig["buildSrc"])


@depend(build)
@task()
def deploy():
    run(["python", "-m", "twine", "upload",
        "--skip-existing", "--repository", "pypi", str(mconfig["buildDist"]) + "/*"])
