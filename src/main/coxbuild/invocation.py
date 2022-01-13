import functools
import pathlib
import subprocess
from dataclasses import dataclass, field

from coxbuild.exceptions import CoxbuildException


@dataclass
class CommandExecutionArgs:
    cmds: list[str]
    env: dict[str, str] | None = None
    cwd: pathlib.Path | None = None
    timeout: float | None = None
    input: str | None = None
    shell: bool = False
    pipe: bool = False


@dataclass
class CommandExecutionResult:
    args: CommandExecutionArgs
    code: int | None = None
    stdout: str = ""
    stderr: str = ""

    def timeout(self) -> bool:
        return self.code is None

    def __bool__(self):
        return self.code == 0


def execmd(args: CommandExecutionArgs) -> CommandExecutionResult:
    try:
        result = subprocess.run(args=args.cmds, env=args.env, cwd=args.cwd, encoding="utf-8", text=True, input=args.input, shell=args.shell,
                                timeout=args.timeout, stdout=subprocess.PIPE if args.pipe else None, stderr=subprocess.PIPE if args.pipe else None)
        return CommandExecutionResult(args, result.returncode, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return CommandExecutionResult(args)


def run(args: CommandExecutionArgs, retry: int = 0, fail: bool = False) -> CommandExecutionResult:
    result = execmd(args)
    if not result:
        for i in range(retry):
            result = execmd(args)
            if result:
                break
    if not fail and not result:
        if result.timeout():
            raise CoxbuildException("Timeout to execute command.")
        else:
            raise CoxbuildException(f"Fail to execute command: exitcode {result.code}.")
    return result
