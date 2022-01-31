import base64
import importlib
import logging
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from types import ModuleType
from urllib import request
from uuid import uuid1

from coxbuild.exceptions import CoxbuildException

from . import Extension

logger = logging.getLogger("extension-loader")


def hashed(src: str):
    return sha256(src.encode()).hexdigest()


def fromModule(module: ModuleType, version: str = "") -> Extension:
    """
    Load extension from module.

    mod@{hashcode}://{module name}@{version}

    :param module: module to load
    :param hashcode: hashcode
    :param version: version
    """
    logger.info("Load extension from module: %s", module.__name__)

    uri = f"mod"

    uri += f"://{module.__name__}"

    rversion = getattr(module, "__version__", "")
    if version and rversion != version:
        raise CoxbuildException("Unmatched version.")
    if rversion:
        uri += f"@{rversion}"
    return Extension(uri, module.__name__, module.__doc__ or "", version, "", module)


def fromSource(src: str, filename: str = "<string>", hashcode: str = "") -> Extension:
    """
    Load extension from source.

    src@{hashcode}://{source code in base64}

    :param src: source code
    :param filename: filename
    :param hashcode: hashcode
    """
    logger.info("Load extension from source: %s...", src[:20])

    rhashcode = hashed(src)
    if hashcode and rhashcode != hashcode:
        raise CoxbuildException("Unmatched hashcode.")

    spec = spec_from_loader(rhashcode, loader=None)
    mod = module_from_spec(spec)

    code = compile(src, filename, "exec")

    exec("from coxbuild.schema import *", mod.__dict__)
    exec(code, mod.__dict__)

    ext = fromModule(mod)
    ext.uri = f"src@{rhashcode}://{base64.b64encode(src.encode()).decode()}"
    ext.hashcode = rhashcode
    return ext


def fromFile(file: Path, hashcode: str = "") -> Extension:
    """
    Load extension from file.

    file@{hashcode}://{file path}

    :param file: file to load
    :param hashcode: hashcode
    """
    logger.info("Load extension from file: %s", str(file))

    src = file.read_text()
    ext = fromSource(src, str(file), hashcode=hashcode)

    ext.name = file.stem
    ext.uri = f"file@{ext.hashcode}://{str(file.resolve())}"
    return ext


def fromUrl(url: str, hashcode: str = "") -> Extension:
    """
    Load extension from url.

    url@{hashcode}://{url}

    :param url: url to load
    :param hashcode: hashcode
    """
    logger.info("Load extension from url: %s", url)

    with request.urlopen(url) as f:
        src = f.read().decode("utf-8")

    ext = fromSource(src, filename=url, hashcode=hashcode)
    ext.uri = f"url@{ext.hashcode}://{url}"
    return ext


def fromGallery(name: str, version: str = "", hashcode: str = "") -> Extension:
    """
    Load extension from gallery.

    ext@{hashcode}://{name}@{version}

    :param name: name of extension
    :param version: version of extension
    :param hashcode: hashcode
    """
    logger.info("Load extension from gallery: %s", name)

    from .gallery import galleries

    gals = galleries()

    for gal in gals:
        ext = gal.load(name, version, hashcode)
        if ext:
            return ext

    raise CoxbuildException(
        f"Failed to load extension from gallery: {name}@{version}")


def load(uri: str):
    splited = uri.split("://", 1)
    if len(splited) != 2:
        schema, path = "module", splited[0]
    else:
        schema, path = splited

    hashcode = schema.split("@", 1)[1] if "@" in schema else ""
    schema = schema.split("@", 1)[0] if "@" in schema else schema

    if schema == "mod":
        items = path.split("@", 1)
        if len(items) != 2:
            name, version = items[0], ""
        else:
            name, version = items
        ext = fromModule(importlib.import_module(name), version)
        return ext
    elif schema == "src":
        src = base64.b64decode(path.encode()).decode()
        ext = fromSource(src, filename="<string>", hashcode=hashcode)
        return ext
    elif schema == "file":
        file = Path(path)
        ext = fromFile(file, hashcode)
        return ext
    elif schema == "url":
        ext = fromUrl(path, hashcode)
        return ext
    elif schema == "ext":
        items = path.split("@", 1)
        if len(items) != 2:
            name, version = items[0], ""
        else:
            name, version = items
        ext = fromGallery(name, version, hashcode)
        return ext
    else:
        raise CoxbuildException(f"Unknown extension schema: {schema}")
