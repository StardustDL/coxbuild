import base64
import os
import shutil
from datetime import timedelta
from pathlib import Path

from coxbuild.extensions import ProjectSettings
from coxbuild.extensions.python import docs as pydocs
from coxbuild.extensions.python import format as pyformat
from coxbuild.extensions.python import package as pypackage
from coxbuild.extensions.python import test as pytest
from coxbuild.pipelines import PipelineContext, beforePipeline
from coxbuild.schema import depend, ext, run, setup, task, teardown


@depend(pypackage.installBuilt)
@task
def demo():
    run(["coxbuild", "--version"])
    run(["coxbuild", "--help"])


demoCmdPre = ["coxbuild", "-vvv", "-D", "./demo"]


@depend(pypackage.installBuilt)
@task
def test_basic():
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
    run([*demoCmdPre, ":ext"])
    run([*demoCmdPre, ":serve"])


@depend(pypackage.installBuilt)
@task
def test_config():
    run([*demoCmdPre, "-f", "config.py", "-c", "name=test", "-c", "id=testid"])


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
def test_ext():
    run([*demoCmdPre, "-f", "ext.py"],
        timeout=timedelta(seconds=3))


@depend(pypackage.installBuilt)
@task
def test_command():
    run([*demoCmdPre, "-f", "command.py"])
    res = run([*demoCmdPre,
              "-f", "command.py", "fail", "retry"], fail=True)
    if res:
        raise Exception("Unexpected success for failing command.")


@depend(pypackage.installBuilt, test_basic, test_lifecycle, test_service, test_ext)
@task
def test_uri():
    run([*demoCmdPre, "-i", "file://lifecycle.py"])

    src = base64.b64encode(
        Path("./demo/buildcox.py").read_text().encode()).decode()
    run([*demoCmdPre, "-i", f"src://{src}"])

    run([*demoCmdPre, "-i", "url://https://raw.githubusercontent.com/StardustDL/coxbuild/master/demo/buildcox.py"])
    run([*demoCmdPre, "-u", "https://raw.githubusercontent.com/StardustDL/coxbuild/master/demo/event.py"])

    run([*demoCmdPre, "-e", "hello"])


@depend(test_basic, test_lifecycle, test_command, test_service, test_builtin, test_event_fs, test_ext, test_uri, test_config)
@task
def integrationtest(): pass


@depend(pytest.test)
@task
def unittest(): pass


@depend(demo, integrationtest, unittest)
@task
async def test():
    await pypackage.uninstallBuilt()
