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

ext(pydocs, pyformat, pypackage, pytest)
ext("file://cbtest.py")

readmeDst = Path("./src/README.md")


@beforePipeline
def initialize(context: PipelineContext):
    project = ProjectSettings(context.config)
    project.docs = Path("./docs/gen/ref")


@pypackage.build.setup
def setupBuild(*args, **kwds):
    shutil.copyfile(Path("README.md"), readmeDst)


@pypackage.build.teardown
def teardownBuild(*args, **kwds):
    os.remove(readmeDst)


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
