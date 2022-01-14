import platform

from coxbuild.schema import group, run

task = group("shell")


def whereCommand(name: str) -> list[str]:
    if "windows" in platform.system().lower():
        res = run(["where.exe", name], pipe=True, fail=True)
        if res:
            return [f.strip() for f in res.stdout.splitlines() if f.strip()]
        else:
            return []
    else:
        res = run(["whereis", name], pipe=True, fail=True)
        if res:
            return [f.strip() for f in res.stdout.split(":")[1].strip().split(" ") if f.strip()]
        else:
            return []


def existCommand(name: str) -> bool:
    return len(whereCommand(name)) > 0


@task
def execute(*args, **kwargs):
    run(*args, **kwargs)
