"""TODO: DOCS CLI"""

import click
from .commands.run import run
from .commands.clear import clear

@click.group()
def cli():
    """Grupo principal para el cli."""

cli.add_command(run)
cli.add_command(clear)
