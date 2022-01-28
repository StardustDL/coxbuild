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


def ext(*exts: ModuleType | str):
    from .extensions.loader import fromModule, load as loadext

    for module in exts:
        if isinstance(module, str):
            module = loadext(module)
        else:
            module = fromModule(module)
        manager.register(module)
