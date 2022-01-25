import pathlib
from dataclasses import asdict
from datetime import timedelta
from typing import Awaitable, Callable

import pip

from .configuration import Configuration, ExecutionState
from .invocation import CommandExecutionArgs, CommandExecutionResult
from .invocation import run
from .pipelines import (Pipeline, PipelineContext, PipelineHook,
                        PipelineResult, TaskContext, TaskHook)
from .services import EventHandler, Service
from .tasks import Task, TaskResult, depend, precond, postcond

service = Service()
pipeline = Pipeline()
config = Configuration()

executionState = ExecutionState(config.section("execution"))


task = pipeline.task
group = pipeline.group
before = pipeline.before
after = pipeline.after
setup = pipeline.setup
teardown = pipeline.teardown
on = service.on
