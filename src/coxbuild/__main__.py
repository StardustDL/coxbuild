from typing import Optional
import click
import logging
from datetime import time


def demo():
    print("""
""")


@click.command()
@click.option("--schema", default=None, help="Schema file name.")
def main(schema: Optional[str] = None) -> None:
    """Coxbuild (https://github.com/StardustDL/coxbuild)."""
    logger = logging.getLogger("main")

    print("Welcome to Coxbuild!")

    if schema is not None:
        with open(schema, encoding="utf8") as f:
            src = "".join(f.readlines())
    else:
        demo()


if __name__ == '__main__':
    main()
