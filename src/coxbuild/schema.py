import importlib
import pathlib
from dataclasses import asdict
from datetime import timedelta
from types import ModuleType
from typing import Awaitable, Callable

from .configuration import Configuration
from .extensions import ProjectSettings
from .invocation import CommandExecutionArgs, CommandExecutionResult, run
from .managers import Manager
from .pipelines import (Pipeline, PipelineContext, PipelineHook,
                        PipelineResult, TaskContext, TaskHook, afterPipeline,
                        afterTask, beforePipeline, beforeTask)
from .runtime import ExecutionState
from .services import EventHandler, Service, on
from .tasks import (after, asafter, asbefore, aspostcond, asprecond, assetup,
                    asteardown, before, depend, group, named, postcond,
                    precond, setup, task, teardown)

manager = Manager()

service = manager.service
pipeline = manager.pipeline
config = manager.config
executionState = manager.executionState


def loadext(module: ModuleType | str):
    if isinstance(module, str):
        module = importlib.import_module(module)
    manager.load(module)
