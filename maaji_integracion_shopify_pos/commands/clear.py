"""TODO: DOCS"""

import click
from ..controllers.locations import DataLocations
from ..controllers.stocky import DataStocky, DataSuppliers
from ..fieldsmapping import FieldMapping

@click.command("data-cache")
def clear_data_cache() -> None:
    """Elimina todos los archvos json que sirven como cache para la automatización"""
    DataLocations.remove_file()
    DataStocky.remove_file()
    DataSuppliers.remove_file()
    FieldMapping.remove_file()

@click.group()
def clear() -> None:
    """Grupo de comandos para la limpieza de datos de la automatización."""

clear.add_command(clear_data_cache)
