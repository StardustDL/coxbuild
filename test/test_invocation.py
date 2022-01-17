from datetime import timedelta
from coxbuild.invocation import CommandExecutionArgs, run
from coxbuild import get_working_directory


def test_run():
    result = run(CommandExecutionArgs(
        ["echo", "abc"], shell=True, cwd=get_working_directory(), pipe=True))
    assert result


def test_fail():
    result = run(CommandExecutionArgs(
        ["cat", "abc.txt"], shell=True, cwd=get_working_directory(), pipe=True), fail=True, retry=1)


def test_timeout():
    result = run(CommandExecutionArgs(
        ["ping", "bing.com"], cwd=get_working_directory(), timeout=timedelta(seconds=0.2), pipe=True), fail=True)
    assert not result
    assert result.timeout
