import logging
import pathlib
import subprocess
from dataclasses import dataclass, field
from datetime import timedelta
from timeit import default_timer as timer

from .exceptions import CoxbuildException

logger = logging.getLogger("invocation")


@dataclass
class CommandExecutionResult:
    """Result for command execution."""
    args: "CommandExecutionArgs"
    """arguments for command execution"""
    duration: timedelta = field(default_factory=timedelta)
    """execution duration"""
    code: int | None = None
    """exit code, None for timeout"""
    stdout: str = ""
    """stdout in text (if pipe)"""
    stderr: str = ""
    """stderr in text (if pipe)"""

    @property
    def timeout(self) -> bool:
        """Return if execution timeout."""
        return self.code is None

    def __bool__(self):
        return self.code == 0

    @property
    def description(self):
        """Return result's description string."""
        return "🟢 SUCCESS" if self else ("🟡 TIMEOUT" if self.timeout else f"🔴 FAILING({self.code})")


def execmd(args: "CommandExecutionArgs"):
    """Execute command and get result."""
    logger.debug(f"Execute command: {args}")

    result = CommandExecutionResult(args)

    tic = timer()
    try:
        subresult = subprocess.run(args=args.cmds, env=args.env, cwd=args.cwd, encoding="utf-8", text=True, input=args.input, shell=args.shell,
                                   timeout=args.timeout.total_seconds() if args.timeout else None, capture_output=args.pipe)
        result.code = subresult.returncode
        result.stdout = subresult.stdout or ""
        result.stderr = subresult.stderr or ""
    except subprocess.TimeoutExpired as te:
        result.stdout = te.stdout or ""
        result.stderr = te.stderr or ""

    result.duration = timedelta(seconds=timer()-tic)
    logger.info(f"Executed command: {args} -> {result}")
    return result


@dataclass
class CommandExecutionArgs:
    """Arguments for command execution."""
    cmds: list[str]
    """command and arguments"""
    env: dict[str, str] | None = None
    """environ"""
    cwd: pathlib.Path | None = None
    """current working directory"""
    timeout: timedelta | None = None
    """maximum execution duration"""
    input: str | None = None
    """text for stdin"""
    shell: bool = False
    """use system shell"""
    pipe: bool = False
    """pipe and collect stdout and stderr"""

    def run(self, retry: int = 0, fail: bool = False) -> CommandExecutionResult:
        """
        Run command.

        retry: the number of times to retry when failing
        fail: do not raise exception when the final result fails
        """

        result = execmd(self)
        if not result:
            for i in range(retry):
                logger.info(f"Retry ({i+1}/{retry}) execute command: {self}")
                result = execmd(self)
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


def run(cmds: list[str], env: dict[str, str] | None = None,
        cwd: pathlib.Path | None = None, timeout: timedelta | None = None,
        input: str | None = None,
        shell: bool = False, pipe: bool = False,
        retry: int = 0, fail: bool = False) -> CommandExecutionResult:
    """
    Run command.

    cmds: command and argument
    env: environ
    cwd: current working directory
    timeout: maximum execution duration
    input: text for stdin
    shell: use system shell
    pipe: pipe and collect stdout and stderr
    retry: the number of times to retry when failing
    fail: do not raise exception when the final result fails
    """
    return CommandExecutionArgs(cmds, env, cwd, timeout, input, shell, pipe).run(retry=retry, fail=fail)
