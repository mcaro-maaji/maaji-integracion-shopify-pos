"""TODO: DOCS CLI"""

import click
from .commands.run import run

@click.group()
def cli():
    """Grupo principal para el cli."""

cli.add_command(run)
