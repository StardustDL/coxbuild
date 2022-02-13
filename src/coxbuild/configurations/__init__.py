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

    def copy(self) -> "Configuration":
        """Copy configuration."""
        return Configuration(self.name, self.data.copy())

    def _getid(self, attr: str) -> str:
        return (self.name + ":" + attr if self.name else attr).lower()

    def __iter__(self):
        pre = ""
        if self.name:
            pre = f"{self.name}:"
        return (key.removeprefix(pre) for key in self.data if key.startswith(pre))

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
        name = name.lower()
        if name not in self.cache:
            self.cache[name] = Configuration(self._getid(name), self.data)
        return self.cache[name]

    def env(self):
        return self.section("env")


class ConfigurationAccessor:
    """Configuration accessor."""

    __configname__ = ""

    def __init__(self, config: Configuration) -> None:
        self.rootConfig = config
        if self.__configname__:
            self.config = config.section(self.__configname__)
        else:
            self.config = config

    def get(self, key: str) -> Any:
        """Get configuration value."""
        return self.config.get(key)

    def getPath(self, key: str) -> Path | None:
        """Get configuration value as Path."""
        value: Path | None | str = self.get(key)
        if isinstance(value, str):
            value = Path(value)
        return value
