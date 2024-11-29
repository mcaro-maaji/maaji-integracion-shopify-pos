"""TODO: DOCS CLI"""

import click
from .commands.run import run_purchase_orders

@click.group()
def cli():
    """Grupo principal para el cli."""

cli.add_command(run_purchase_orders)

if __name__ == "__main__":
    cli()
