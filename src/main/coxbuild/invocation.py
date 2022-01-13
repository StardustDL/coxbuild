import functools
import logging
import pathlib
import subprocess
from dataclasses import dataclass, field
from datetime import timedelta
from socket import timeout
from timeit import default_timer as timer

from coxbuild.exceptions import CoxbuildException

logger = logging.getLogger("invocation")


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
    duration: timedelta = field(default_factory=timedelta)
    code: int | None = None
    stdout: str = ""
    stderr: str = ""

    @property
    def timeout(self) -> bool:
        return self.code is None

    def __bool__(self):
        return self.code == 0

    @property
    def description(self):
        return "🟢 SUCCESS" if self else ("🟡 TIMEOUT" if self.timeout else f"🔴 FAILING({self.code})")


def execmd(args: CommandExecutionArgs) -> CommandExecutionResult:
    logger.debug(f"Execute command: {args}")

    result = CommandExecutionResult(args)

    tic = timer()
    try:
        subresult = subprocess.run(args=args.cmds, env=args.env, cwd=args.cwd, encoding="utf-8", text=True, input=args.input, shell=args.shell,
                                   timeout=args.timeout, stdout=subprocess.PIPE if args.pipe else None, stderr=subprocess.PIPE if args.pipe else None)
        result.code = subresult.returncode
        result.stdout = subresult.stdout if subresult.stdout else ""
        result.stderr = subresult.stderr if subresult.stderr else ""
    except subprocess.TimeoutExpired as te:
        result.stdout = te.stdout if te.stdout else ""
        result.stderr = te.stderr if te.stderr else ""

    result.duration = timedelta(timer()-tic)
    logger.info(f"Executed command: {args} -> {result}")
    return result


def run(args: CommandExecutionArgs, retry: int = 0, fail: bool = False) -> CommandExecutionResult:
    result = execmd(args)
    if not result:
        for i in range(retry):
            logger.info(f"Retry ({i+1}/{retry}) execute command: {args}")
            result = execmd(args)
            if result:
                break
    if not fail and not result:
        if result.timeout:
            raise CoxbuildException("\n".join([
                f"Timeout to execute command ({result.duration}).",
                "Standard Output:",
                result.stdout,
                "Standard Error:",
                result.stderr]))
        else:
            raise CoxbuildException("\n".join([
                f"Fail to execute command ({result.duration}): exitcode {result.code}.",
                "Standard Output:",
                result.stdout,
                "Standard Error:",
                result.stderr]))
    return result
