"""TODO: DOCS"""

from datetime import datetime, timedelta
import click
from ..controllers import purchase_order

@click.command()
@click.option("--store", default="maaji_co_test", help="seleccione la tienda shopify.")
@click.option("--env", default="uat", help="Entorno de Dynamics 365. [prod | uat]")
@click.option("--date", default=datetime.now(), help="Fecha para buscar las facturas en el servicio D365.")
@click.option("--days", default=1, help="Dias posteriores a la fecha programada en --date para buscar las facturas.")
def run_purchase_orders(store, env, date, days):
    """Comando para ejecutar el servicio de crear ordenes de compra mediante D365 y Stocky"""
    date_start = datetime.strptime(date, "%d/%m/%Y")
    date_end = date_start + timedelta(days)
    payload = purchase_order.DataApiPayload("AM", date_start, date_end)
    purchase_order.create_from_service(payload, store, env)
