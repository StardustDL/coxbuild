from coxbuild.configurations import Configuration
from coxbuild.configurations.builders import (DictionaryConfigurationBuilder,
                                              EnvironmentConfigurationBuilder)


def test_nested_dict():
    c = Configuration()

    DictionaryConfigurationBuilder({
        "a": 1,
        "b": {
            "c": 2,
        },
        "d": {
            "__keep__": None,
            "e": 3,
        },
    }).build(c)

    assert c["a"] == 1
    assert c["b:c"] == 2
    assert isinstance(c["d"], dict)
    assert c["d"]["e"] == 3
    assert "__keep__" not in c["d"]


def test_env():
    c = Configuration()
    EnvironmentConfigurationBuilder().build(c)
    assert c.env().data
