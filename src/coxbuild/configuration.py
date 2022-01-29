import os
from pathlib import Path
from typing import Any


class Configuration:
    """Build configuration, entry key is case-insensitive."""

    def __init__(self, name: str = "", data: dict[str, Any] | None = None) -> None:
        """
        Create configuration.

        name: section name
        data: data source
        """
        self.name = name
        self.data: dict[str, Any] = data if data is not None else {}
        self.cache: dict[str, Configuration] = {}
        if not self.name:
            self.loadenv()

    def copy(self) -> "Configuration":
        """Copy configuration."""
        return Configuration(self.name, self.data.copy())

    def _getid(self, attr: str) -> str:
        return (self.name + ":" + attr if self.name else attr).lower()

    def __iter__(self):
        pre = ""
        if self.name:
            pre = f"{self.name}:"
        return (key for key in self.data if key.startswith(pre))

    def get(self, key: str) -> Any | None:
        id = self._getid(key)
        return self.data.get(id)

    def __getitem__(self, key: str) -> Any:
        id = self._getid(key)
        return self.data[id]

    def __setitem__(self, key: str, value: Any) -> None:
        id = self._getid(key)
        self.data[id] = value

    def __delitem__(self, key: str) -> None:
        id = self._getid(key)
        del self.data[id]

    def section(self, name: str):
        """
        Get sub-section.

        name: sub-section name
        """
        if name not in self.cache:
            self.cache[name] = Configuration(self._getid(name), self.data)
        return self.cache[name]

    def env(self):
        """Get environ section."""
        return self.section("env")

    def envbuild(self):
        """Get environ:coxbuild section."""
        return self.env().section("coxbuild")

    def loadenv(self):
        """Load environ section from os."""
        env = self.env()
        for key in os.environ:
            env[key] = os.getenv(key)


class ConfigurationAccessor:
    """Configuration accessor."""

    __configname__ = ""

    def __init__(self, config: Configuration) -> None:
        self.rootConfig = config
        if self.__configname__:
            self.config = config.section(self.__configname__)
            self.fallback = config.envbuild().section(self.__configname__)
        else:
            self.config = config
            self.fallback = config.envbuild()

    def get(self, key: str) -> Any:
        """Get configuration value (or fallback)."""
        return self.config.get(key) or self.fallback.get(key)

    def getPath(self, key: str) -> Path | None:
        """Get configuration value (or fallback) as Path."""
        value: Path | None | str = self.get(key)
        if isinstance(value, str):
            value = Path(value)
        return value
