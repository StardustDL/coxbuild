import inspect
from types import ModuleType
from uuid import uuid1
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path
from coxbuild.pipelines import Pipeline, PipelineHook
from coxbuild.services import EventHandler, Service

from coxbuild.tasks import Task


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
                    pipeline.register(t)
            case EventHandler() as eh:
                service.register(eh)
            case PipelineHook() as ph:
                pipeline.hook(ph)
