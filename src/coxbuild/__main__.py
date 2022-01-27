import logging
import os
from pathlib import Path

import click

from coxbuild import __version__


@click.command()
@click.argument("tasks", default=None, nargs=-1)
@click.option('-D', '--directory', type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path), default=".", help="Path to working directory.")
@click.option('-f', '--file', default="buildcox.py", help="Schema file name.")
@click.version_option(__version__, package_name="coxbuild", prog_name="coxbuild", message="%(prog)s v%(version)s, written by StardustDL.")
@click.option('-v', '--verbose', count=True, default=0, type=click.IntRange(0, 5))
def main(ctx=None, tasks: list[str] | None = None, directory: Path = ".", file: str = "buildcox.py", verbose: int = 0) -> None:
    """
    Coxbuild is a tiny python-script-based build automation tool, an alternative to make, psake and so on.

    Source Project: https://github.com/StardustDL/coxbuild
    """
    click.echo(f"Welcome to Coxbuild v{__version__}!")

    loggingLevel = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
        5: logging.NOTSET
    }[verbose]
    logging.basicConfig(level=loggingLevel)
    logger = logging.getLogger("Cli-Main")
    logger.debug(f"Logging level: {loggingLevel}")

    os.chdir(str(Path(str(directory)).resolve()))
    schemafile = Path(file)
    logger.debug(f"Schema file: {click.format_filename(schemafile)}")
    if not schemafile.exists():
        raise click.ClickException("Coxbuild schema NOT FOUND.")

    from coxbuild import managers, schema
    schema.manager.load(managers.loadModuleFromFile(schemafile))

    exit(0 if schema.manager.execute(*(tasks or [])) else 1)


if __name__ == '__main__':
    main()
