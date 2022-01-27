import pathlib
from dataclasses import asdict
from datetime import timedelta
from types import ModuleType
from typing import Awaitable, Callable

from .managers import Manager
from .configuration import Configuration, ExecutionState
from .invocation import CommandExecutionArgs, CommandExecutionResult, run
from .pipelines import (Pipeline, PipelineContext, PipelineHook,
                        PipelineResult, TaskContext, TaskHook)
from .services import EventHandler, Service, on
from .tasks import task, group, named, depend, setup, teardown, before, after, precond, postcond, asprecond, assetup, aspostcond, asteardown, asbefore, asafter
from .pipelines import beforePipeline, beforeTask, afterPipeline, afterTask

manager = Manager()

service = manager.service
pipeline = manager.pipeline
config = manager.config
executionState = manager.executionState


def loadext(module: ModuleType):
    manager.load(module)
