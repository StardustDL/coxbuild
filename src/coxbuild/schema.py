import importlib
import pathlib
from dataclasses import asdict
from datetime import timedelta
from types import ModuleType
from typing import Awaitable, Callable

from .configuration import Configuration
from .extensions import Extension, ProjectSettings
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


def ext(extension: ModuleType | str) -> Extension:
    from .extensions.loader import fromModule
    from .extensions.loader import load as loadext

    if isinstance(extension, str):
        print(f"Loading extension from {extension}")
        extension = loadext(extension)
    else:
        print(f"Loading extension from module {extension.__name__}")
        extension = fromModule(extension)
    manager.register(extension)
    return extension
