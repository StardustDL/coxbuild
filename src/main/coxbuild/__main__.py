import click
import logging
from datetime import time
from . import __version__


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(__version__, package_name="coxbuild", prog_name="coxbuild", message="%(prog)s v%(version)s, written by StardustDL.")
@click.option('-v', '--verbose', count=True, default=0, type=click.IntRange(0, 5))
def main(ctx=None, verbose: int = 0) -> None:
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


if __name__ == '__main__':
    main()
