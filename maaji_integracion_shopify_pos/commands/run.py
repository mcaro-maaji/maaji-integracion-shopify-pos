"""TODO: DOCS"""

from datetime import datetime, timedelta
import click
from ..controllers import purchase_order
from ..config import KeySitesShopifyStores

@click.command("purchase-orders")
@click.option("--store", default="maaji_co_test", help="seleccione la tienda shopify.")
@click.option("--date", help="Fecha del día para buscar las facturas en el servicio D365.")
@click.option("--env", default="prod", help="Entorno de Dynamics 365. [prod | uat]")
@click.option("--days", default=1, help="Cantidad de días posteriores a la fecha --date.")
def run_purchase_orders(store: KeySitesShopifyStores, env, date, days):
    """Comando para ejecutar el servicio de crear ordenes de compra mediante D365 y Stocky"""
    date_start = datetime.strptime(date, "%d/%m/%Y")
    date_end = date_start + timedelta(days, seconds=-1)
    print(date_start.isoformat(), date_end.isoformat())
    payload = purchase_order.DataApiPayload("AM", date_start, date_end)
    purchase_order.create_from_service(payload, store, env)

@click.group()
def run():
    """Comando para ejecutar catacteristicas de la integración."""

run.add_command(run_purchase_orders)
