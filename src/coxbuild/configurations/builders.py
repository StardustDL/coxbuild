import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml

from . import Configuration


class ConfigurationBuilder(ABC):
    @abstractmethod
    def build(self, config: Configuration) -> None: pass


class EnvironmentConfigurationBuilder(ConfigurationBuilder):
    def build(self, config: Configuration) -> None:
        env = config.env()
        envbuild = env.section("coxbuild")
        for key in os.environ:
            env[key] = os.getenv(key)
        for key in envbuild:
            config[key] = envbuild[key]


class DictionaryConfigurationBuilder(ConfigurationBuilder):
    """
    Use dictionary to build configuration.

    Nested dictionary will be converted to a subsection.
    To avoid this behavior, use an entry with key '__keep__'.
    """

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__()
        self.data = data

    def build(self, config: Configuration) -> None:
        for key in self.data:
            value = self.data[key]

            if isinstance(value, dict):
                if "__keep__" in value:
                    del value["__keep__"]
                    config[key] = value
                else:
                    sub = config.section(key)
                    DictionaryConfigurationBuilder(value).build(sub)
            else:
                config[key] = value


class JsonConfigurationBuilder(ConfigurationBuilder):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path

    def build(self, config: Configuration) -> None:
        if not self.path.exists():
            return
        DictionaryConfigurationBuilder(
            json.loads(self.path.read_text())).build(config)


class YamlConfigurationBuilder(ConfigurationBuilder):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path

    def build(self, config: Configuration) -> None:
        if not self.path.exists():
            return
        DictionaryConfigurationBuilder(
            yaml.safe_load(self.path.read_text())).build(config)


class ConfigurationBuilderCollection(ConfigurationBuilder):
    def __init__(self) -> None:
        super().__init__()
        self.builders: list[ConfigurationBuilder] = []

    def add(self, builder: ConfigurationBuilder) -> "ConfigurationBuilderCollection":
        self.builders.append(builder)
        return self

    def build(self, config: Configuration) -> None:
        for builder in self.builders:
            builder.build(config)


def getDefaultBuilder() -> ConfigurationBuilderCollection:
    """Use environment variables and file buildcox.[json/yaml] to build configuration."""
    return ConfigurationBuilderCollection() \
        .add(EnvironmentConfigurationBuilder()) \
        .add(JsonConfigurationBuilder(Path("buildcox.json"))) \
        .add(YamlConfigurationBuilder(Path("buildcox.yaml"))) \
        .add(YamlConfigurationBuilder(Path("buildcox.yml")))
