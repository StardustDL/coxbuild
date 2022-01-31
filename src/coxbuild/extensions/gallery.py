import os
from abc import ABC, abstractmethod
from asyncio.log import logger
from pathlib import Path

from . import Extension


class ExtensionGallery(ABC):
    """Extension gallery."""
    @abstractmethod
    def load(self, name: str, version: str = "", hashcode: str = "") -> Extension | None:
        pass


class UriExtensionGallery(ExtensionGallery):
    """Extension gallery by uri."""
    @abstractmethod
    def geturi(self, name: str, version: str = "", hashcode: str = "") -> str | None:
        pass

    def load(self, name: str, version: str = "", hashcode: str = "") -> Extension | None:
        from .loader import load as loadext

        try:
            uri = self.geturi(name, version, hashcode)
            if not uri:
                return None
            ext = loadext(uri)
            ext.uri = f"ext@{ext.hashcode}://{name}@{version}"
            return ext
        except Exception as ex:
            logger.warning(
                f"Failed to load extension from gallery {self}: {ex}")
            return None


class UrlExtensionGallery(UriExtensionGallery):
    """Extension gallery by url."""
    @abstractmethod
    def geturl(self, name: str, version: str = "", hashcode: str = "") -> str | None:
        pass

    def geturi(self, name: str, version: str = "", hashcode: str = "") -> str | None:
        url = self.geturl(name, version, hashcode)
        if not url:
            return None
        return f"url@{hashcode}://{url}" if hashcode else f"url://{url}"


class DirectoryExtensionGallery(UriExtensionGallery):
    """Extension gallery by directory."""

    def __init__(self, path: Path):
        self.path = path.resolve()

    def geturi(self, name: str, version: str = "", hashcode: str = "") -> str | None:
        sub = str(self.path.joinpath(f"{name}.py").resolve())
        return f"file@{hashcode}://{sub}" if hashcode else f"file://{sub}"


class GitHubExtensionGallery(UrlExtensionGallery):
    """Extension gallery by GitHub repository."""

    def __init__(self, repo: str = "StardustDL/coxbuild-ext-gallery", defaultVersion: str = "main") -> None:
        super().__init__()
        self.repo = repo
        self.defaultVersion = defaultVersion

    def geturl(self, name: str, version: str = "", hashcode: str = "") -> str | None:
        if not version:
            version = self.defaultVersion
        return f"https://raw.githubusercontent.com/{self.repo}/{version}/exts/{name}.py"


class JsDelivrExtensionGallery(UrlExtensionGallery):
    """Extension gallery by GitHub repository on jsDelivr CDN."""

    def __init__(self, repo: str = "StardustDL/coxbuild-ext-gallery", defaultVersion: str = "main") -> None:
        super().__init__()
        self.repo = repo
        self.defaultVersion = defaultVersion

    def geturl(self, name: str, version: str = "", hashcode: str = "") -> str | None:
        if not version:
            version = self.defaultVersion
        return f"https://cdn.jsdelivr.net/gh/{self.repo}@{version}/exts/{name}.py"


class GiteeExtensionGallery(UrlExtensionGallery):
    """Extension gallery by Gitee repository."""

    def __init__(self, repo: str = "stardustdl/coxbuild-ext-gallery", defaultVersion: str = "main") -> None:
        super().__init__()
        self.repo = repo
        self.defaultVersion = defaultVersion

    def geturl(self, name: str, version: str = "", hashcode: str = "") -> str | None:
        if not version:
            version = self.defaultVersion
        return f"https://gitee.com/{self.repo}/raw/{version}/exts/{name}.py"


_galleries: list[ExtensionGallery] = []


def galleries():
    """
    Get extension galleries.

    From COXBUILD_GALLERY environment variable.
        GitHub provider: github@reponame
        Gitee provider: gitee@reponame
        Directory provider: directory@directory/path
    """
    if _galleries:
        return _galleries
    env = os.getenv("COXBUILD_GALLERY", "").split(";")

    for item in env:
        item = item.strip()
        if not item:
            continue

        try:
            entry = item.split("@", 1)
            if len(entry) != 2:
                type, name = "directory", entry[0]
            else:
                type, name = entry

            match type.lower():
                case "directory":
                    _galleries.append(DirectoryExtensionGallery(Path(name)))
                case "github":
                    _galleries.append(JsDelivrExtensionGallery(name))
                    _galleries.append(GitHubExtensionGallery(name))
                case "gitee":
                    _galleries.append(GiteeExtensionGallery(name))
        except:
            logger.error(f"Failed to add extension gallery: {item}")

    _galleries.append(GiteeExtensionGallery())
    _galleries.append(JsDelivrExtensionGallery())
    _galleries.append(GitHubExtensionGallery())

    return _galleries
