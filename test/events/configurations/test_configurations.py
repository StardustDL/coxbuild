from coxbuild.configurations import Configuration


def test_config():
    c = Configuration()

    s = c.section("test")
    s["a"] = 1

    assert s["a"] == 1
    assert c["test:a"] == 1
