import asyncio
import inspect
import logging
import pathlib
from dataclasses import dataclass, field
from importlib.util import module_from_spec, spec_from_loader
from types import ModuleType

from coxbuild.exceptions import CoxbuildException

from .configuration import Configuration
from .extensions import Extension
from .pipelines import Pipeline, PipelineHook, PipelineResult
from .runtime import ExecutionState
from .services import EventHandler, Service
from .tasks import Task

logger = logging.getLogger("managers")


@dataclass
class Manager:
    """Manage extensions and execution."""
    extensions: dict[str, Extension] = field(default_factory=dict)

    def copy(self) -> "Manager":
        return Manager(extensions=self.extensions)

    def register(self, ext: Extension):
        if ext.uri not in self.extensions:
            self.extensions[ext.uri] = ext
        else:
            logger.warning(f"Register existed extensions {ext.uri}.")

    def _load(self, *exts: Extension, pipeline: Pipeline, service: Service) -> None:
        def regTask(t: Task):
            if t.name in pipeline.tasks:
                ot = pipeline.tasks.pop(t.name)
                logger.warning(
                    f"Replace registered task: {ot.name}.")
            logger.debug(
                f"Registering task: {t.name} in {ext.name}({ext.uri}).")
            t.extension = ext
            pipeline.register(t)

        for ext in exts:
            logger.debug(f"Import extension: {ext.name}({ext.uri})")
            for t in ext.tasks:
                regTask(t)
            for eh in ext.events:
                logger.debug(
                    f"Registering event handler: {eh.name} in {ext.name}({ext.uri}).")
                eh.extension = ext
                service.register(eh)
                regTask(eh.handler)
            for ph in ext.pipelineHooks:
                logger.debug(
                    f"Registering pipeline hook: in {ext.name}.")
                ph.extension = ext
                pipeline.hook(ph)
            logger.debug(f"Imported extension: {ext.name}({ext.uri})")

    async def executeAsync(self, *tasks: str, config: Configuration = None) -> PipelineResult:
        from coxbuild.extensions import builtin
        from coxbuild.extensions.loader import fromModule

        pipeline = Pipeline()
        config = config or Configuration()
        service = Service()

        executionState = ExecutionState(config)
        executionState.manager = self
        executionState.configuration = config
        executionState.service = service
        executionState.pipeline = pipeline

        self._load(*self.extensions.values(), fromModule(builtin),
                   pipeline=pipeline, service=service)
        runner = pipeline(*(tasks or ["default"]))
        runner.context.config = config
        return await runner

    def execute(self, *tasks: str, config: Configuration = None) -> PipelineResult:
        return asyncio.run(self.executeAsync(*tasks, config=config))
