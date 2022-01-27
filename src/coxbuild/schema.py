import pathlib
from dataclasses import asdict
from datetime import timedelta
from types import ModuleType
from typing import Awaitable, Callable

import pip

from .configuration import Configuration, ExecutionState
from .invocation import CommandExecutionArgs, CommandExecutionResult, run
from .pipelines import (Pipeline, PipelineContext, PipelineHook,
                        PipelineResult, TaskContext, TaskHook)
from .services import EventHandler, Service, on
from .tasks import task, group, named, depend, setup, teardown, before, after, precond, postcond, asprecond, assetup, aspostcond, asteardown, asbefore, asafter
from .pipelines import beforePipeline, beforeTask, afterPipeline, afterTask

service = Service()
pipeline = Pipeline()
config = Configuration()

executionState = ExecutionState(config.section("execution"))


def loadext(module: ModuleType):
    from .builder import loadFromModule

    loadFromModule(module, pipeline, service)
