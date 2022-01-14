import logging
import os
from pathlib import Path

import click

from coxbuild import __version__


@click.command()
@click.argument("tasks", default=None, nargs=-1)
@click.option('-D', '--directory', type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path), default=".", help="Path to working directory.")
@click.option('-f', '--file', default="coxbuild.py", help="Schema file name.")
@click.version_option(__version__, package_name="coxbuild", prog_name="coxbuild", message="%(prog)s v%(version)s, written by StardustDL.")
@click.option('-v', '--verbose', count=True, default=0, type=click.IntRange(0, 5))
def main(ctx=None, tasks: list[str] | None = None, directory: Path = ".", file: str = "coxbuild.py", verbose: int = 0) -> None:
    """Coxbuild (https://github.com/StardustDL/coxbuild)"""
    click.echo(f"Welcome to Coxbuild v{__version__}!")

    logger = logging.getLogger("Cli-Main")

    loggingLevel = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
        5: logging.NOTSET
    }[verbose]

    logging.basicConfig(level=loggingLevel)

    logger.debug(f"Logging level: {loggingLevel}")

    os.chdir(str(Path(str(directory)).absolute()))

    schemafile = Path(file)

    logger.debug(f"Schema file: {click.format_filename(schemafile)}")

    if not schemafile.exists():
        raise click.ClickException("Coxbuild schema NOT FOUND.")

    src = schemafile.read_text(encoding="utf-8")

    import coxbuild.schema

    exec(src, {
        "task": coxbuild.schema.task,
        "depend": coxbuild.schema.depend,
        "run": coxbuild.schema.run,
        "group": coxbuild.schema.group,
        "precond": coxbuild.schema.precond,
        "postcond": coxbuild.schema.postcond,
        "invoke": coxbuild.schema.invoke,
        "before": coxbuild.schema.before,
        "after": coxbuild.schema.after,
        "setup": coxbuild.schema.setup,
        "teardown": coxbuild.schema.teardown,
    })

    if not tasks:
        tasks = ["default"]

    result = coxbuild.schema.pipeline.invoke(*tasks)

    if result:
        exit(0)
    else:
        exit(1)


if __name__ == '__main__':
    main()
