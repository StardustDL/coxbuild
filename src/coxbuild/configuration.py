import os
from typing import Any


class Configuration:
    """Build configuration."""

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

    def _getid(self, attr: str) -> str:
        return self.name + ":" + attr if self.name else attr

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

    def loadenv(self):
        """Load environ section from os."""
        env = self.env()
        for key in os.environ:
            env[key] = os.getenv(key)


class ExecutionState:
    def __init__(self, config: Configuration) -> None:
        self.config = config

    @property
    def unmatchedTasks(self) -> list[str]:
        """Unmatched task names."""
        return self.config.get("unmatchedTasks") or []

    @unmatchedTasks.setter
    def unmatchedTasks(self, value: list[str]) -> None:
        self.config["unmatchedTasks"] = value
