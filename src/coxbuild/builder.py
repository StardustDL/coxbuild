import inspect
import logging
from types import ModuleType
from uuid import uuid1
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path
from coxbuild.pipelines import Pipeline, PipelineHook
from coxbuild.services import EventHandler, Service

from coxbuild.tasks import Task

logger = logging.getLogger("builder")


def loadModule(file: Path):
    spec = spec_from_loader(file.stem, loader=None)
    mod = module_from_spec(spec)

    code = compile(file.read_text(encoding="utf-8"), file, "exec")

    exec(code, mod.__dict__)

    return mod


def loadFromModule(module: ModuleType, pipeline: Pipeline, service: Service):
    for name, member in inspect.getmembers(module):
        if name.startswith("_"):
            continue

        match member:
            case Task() as t:
                if t.name not in pipeline.tasks:
                    logger.debug(
                        f"Registering task: {t.name} in {module.__name__}.",)
                    pipeline.register(t)
                else:
                    logger.debug(
                        f"Ignored registered task: {t.name} in {module.__name__}.",)
            case EventHandler() as eh:
                if eh.name not in service.handlers:
                    logger.debug(
                        f"Registering event handler: {eh.name} in {module.__name__}.",)
                    service.register(eh)
                else:
                    logger.debug(
                        f"Ignored registered event handler: {eh.name} in {module.__name__}.",)
            case PipelineHook() as ph:
                pipeline.hook(ph)
