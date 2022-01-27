import os
import shutil
from datetime import timedelta
from pathlib import Path

from coxbuild.extensions import projectSettings
from coxbuild.extensions.python import settings, docs as pydocs, format as pyformat, package as pypackage, test as pytest
from coxbuild.schema import depend, loadext, run, setup, task, teardown

loadext(pydocs)
loadext(pyformat)
loadext(pypackage)
loadext(pytest)

readmeDst = Path("./src/README.md")

projectSettings.docs = Path("./docs/gen/ref")


@pypackage.build.setup
def setupBuild():
    shutil.copyfile(Path("README.md"), readmeDst)


@pypackage.build.teardown
def teardownBuild():
    os.remove(readmeDst)


@depend(pypackage.installBuilt)
@task
def demo():
    run(["coxbuild", "--version"])
    run(["coxbuild", "--help"])


demoCmdPre = ["coxbuild", "-vvv", "-D", "./demo"]


@depend(pypackage.installBuilt)
@task
def test_build():
    run(["coxbuild", "-vvvvv", "-D", "./demo"])
    res = run([*demoCmdPre, "-f", "fail.py"], fail=True)
    if res:
        raise Exception("Unexpected success for failing build.")
    res = run([*demoCmdPre, "-f", "fail.py", "default2"], fail=True)
    if res:
        raise Exception("Unexpected success for failing build.")
    run([*demoCmdPre, "a"])
    run([*demoCmdPre, "b"])


@depend(pypackage.installBuilt)
@task
def test_builtin():
    run([*demoCmdPre, ":list"])
    run([*demoCmdPre, ":serve"])


@depend(pypackage.installBuilt)
@task
def test_lifecycle():
    run([*demoCmdPre, "-f", "lifecycle.py"])


@depend(pypackage.installBuilt)
@task
def test_service():
    run([*demoCmdPre, "-f", "event.py", ":serve"])


@depend(pypackage.installBuilt)
@task
def test_event_fs():
    run([*demoCmdPre, "-f", "filewatch.py", ":serve"],
        timeout=timedelta(seconds=3))


@depend(pypackage.installBuilt)
@task
def test_command():
    run([*demoCmdPre, "-f", "command.py"])
    res = run([*demoCmdPre,
              "-f", "command.py", "fail", "retry"], fail=True)
    if res:
        raise Exception("Unexpected success for failing command.")


@depend(test_build, test_lifecycle, test_command, test_service, test_builtin, test_event_fs)
@task
def integrationtest(): pass


@depend(pytest.test)
@task
def unittest(): pass


@depend(demo, integrationtest, unittest)
@task
async def test():
    await pypackage.uninstallBuilt()


@depend(pydocs.apidoc)
@task
def docs(): pass


@depend(pypackage.deploy)
@task
def deploy(): pass


@depend(pypackage.restore, pypackage.build)
@task
def build(): pass


@depend(pyformat.format)
@task
def format(): pass


@depend(build)
@task
def default(): pass


@task
def serdoc():
    run(["docsify", "serve", "docs"], shell=True, fail=True)
