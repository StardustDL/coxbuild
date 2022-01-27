import asyncio
import inspect
import logging
import pathlib
from dataclasses import dataclass, field
from importlib.util import module_from_spec, spec_from_loader
from types import ModuleType

from coxbuild.configuration import Configuration, ExecutionState
from coxbuild.pipelines import Pipeline, PipelineHook
from coxbuild.services import EventHandler, Service
from coxbuild.tasks import Task

logger = logging.getLogger("managers")


def loadModuleFromSource(src: str, filename: str, modname: str):
    spec = spec_from_loader(modname, loader=None)
    mod = module_from_spec(spec)

    code = compile(src, filename, "exec")

    exec(code, mod.__dict__)

    return mod


def loadModuleFromFile(file: pathlib.Path):
    return loadModuleFromSource(file.read_text(encoding="utf-8"), str(file), file.stem)


@dataclass
class Manager:
    pipeline: Pipeline = field(default_factory=Pipeline)
    service: Service = field(default_factory=Service)
    config: Configuration = field(default_factory=Configuration)

    executionState: ExecutionState = field(init=False)

    def __post_init__(self):
        self.executionState = ExecutionState(self.config.section("execution"))

    def copy(self) -> "Manager":
        return Manager(
            pipeline=self.pipeline.copy(),
            service=self.service.copy(),
            config=self.config.copy()
        )

    def loadBuiltin(self):
        from coxbuild.extensions import builtin
        self.load(builtin)

    def load(self, module: ModuleType) -> None:
        for name, member in inspect.getmembers(module):
            if name.startswith("_"):
                continue

            match member:
                case Task() as t:
                    if t.name not in self.pipeline.tasks:
                        logger.debug(
                            f"Registering task: {t.name} in {module.__name__}.",)
                        self.pipeline.register(t)
                    else:
                        logger.debug(
                            f"Ignored registered task: {t.name} in {module.__name__}.",)
                case EventHandler() as eh:
                    if eh.name not in self.service.handlers:
                        logger.debug(
                            f"Registering event handler: {eh.name} in {module.__name__}.",)
                        self.service.register(eh)
                    else:
                        logger.debug(
                            f"Ignored registered event handler: {eh.name} in {module.__name__}.",)
                case PipelineHook() as ph:
                    logger.debug(
                        f"Registering pipeline hook: in {module.__name__}.",)
                    self.pipeline.hook(ph)

    def execute(self, *tasks: str) -> bool:
        self.loadBuiltin()

        async def wrapper():
            return await self.pipeline(*(tasks or ["default"]))

        result = asyncio.run(wrapper())

        return bool(result)
