import importlib
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from uuid import uuid1

from coxbuild.exceptions import CoxbuildException
from . import Extension
from types import ModuleType
from hashlib import sha256
from urllib import request

DEFAULT_VERSION = "0.0.0"


def fromModule(module: ModuleType) -> Extension:
    version = getattr(module, "__version__", DEFAULT_VERSION)
    return Extension(f"module://{module.__name__}@{version}", module.__name__, module.__doc__ or "", version, module)


def fromSource(src: str, filename: str = "<string>") -> Extension:
    hashed = sha256(src.encode()).hexdigest()
    name = f"ext-{hashed}"

    spec = spec_from_loader(name, loader=None)
    mod = module_from_spec(spec)

    code = compile(src, filename, "exec")

    exec("from coxbuild.schema import *", mod.__dict__)
    exec(code, mod.__dict__)

    ext = fromModule(mod)
    ext.uri = f"source://{hashed}"
    return ext


def fromFile(file: Path) -> Extension:
    src = file.read_text()
    ext = fromSource(src, str(file))
    ext.name = file.stem
    ext.uri = f"file://{str(file)}"
    return ext


def fromUrl(url: str) -> Extension:
    with request.urlopen(url) as f:
        src = f.read().decode("utf-8")

    ext = fromSource(src)
    ext.uri = f"url://{url}"
    return ext


def load(uri: str):
    splited = uri.split("://", 1)
    if len(splited) != 2:
        schema, path = "module", splited[0]
    else:
        schema, path = splited

    match schema:
        case "module":
            items = path.split("@", 1)
            if len(items) != 2:
                name, version = items[0], None
            else:
                name, version = items
            ext = fromModule(importlib.import_module(name))
            if version and ext.version != version:
                raise CoxbuildException(
                    f"Failed to load extension {uri}: unmatched version, expected {version}, got {ext.version}.")
            return ext
        case "source":
            return fromSource(path)
        case "file":
            return fromFile(Path(path))
        case "url":
            return fromUrl(path)
        case _:
            raise ValueError(f"Unknown schema: {schema}")
