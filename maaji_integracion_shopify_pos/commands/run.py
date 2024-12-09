"""TODO: DOCS"""

from datetime import datetime, timedelta
import click
from ..controllers import purchase_order
from ..config import key_sites_shopify_stores as key_stores
from ..utils import ENVIRONMENT

dt_formats = ("%d/%m/%Y", "%d/%m/%YT%H:%M:%S", "%d/%m/%Y %H:%M:%S",
                    "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%H:%M:%S")

class DateOrDeltaTime(click.DateTime):
    """Crea un tipo de dato timedelta o datetime como parametro de CLI."""
    name = '[datetime | timedelta]'

    def convert(self, value: str | datetime | timedelta, param, ctx):
        if isinstance(value, (datetime, timedelta)):
            return value
        try:
            # Format 1: # weeks, # days, hours:minutes:seconds:microseconds:milliseconds
            # Format 2: # days, hours:minutes:seconds:microseconds:milliseconds
            value_parts = value.split(", ")
            time_parts = value_parts.pop()
            if len(value_parts) == 2:
                [weeks_part, days_part] = value_parts
            elif len(value_parts) == 1:
                [weeks_part, days_part] = (None, value_parts[0])
            else:
                [weeks_part, days_part] = (None, None)

            num_weeks = 0. if weeks_part is None else float(weeks_part.replace(" weeks", ""))
            num_days = 0. if days_part is None else float(days_part.replace(" days", ""))
            num_times = map(float, time_parts.split(":"))
            keys = ("weeks", "days", "hours", "minutes", "seconds", "microseconds", "milliseconds")
            items = zip(keys, [num_weeks, num_days, *num_times])
            kwargs = {}
            kwargs.update(items)
            return timedelta(**kwargs)
        except ValueError:
            return super().convert(value, param, ctx)

@click.command("purchase-orders")
@click.option("-s", "--store", type=click.Choice(key_stores), required=True)
@click.option("-e", "--env", type=click.Choice(("uat", "prod")), default="prod")
@click.option("-t", "-d", "--time-end", "--date-end", "--date", type=DateOrDeltaTime(dt_formats))
@click.option("-ts", "-ds", "--time-start", "--date-start", type=DateOrDeltaTime(dt_formats))
def run_purchase_orders(store, env, time_end, time_start):
    """Ejecuta el servicio de crear ordenes de compra Stocky mediante el servicio D365."""
    if ENVIRONMENT != "prod" and store in ["maaji_pos", "maaji_pos_outlet"]:
        msg = "No se puede ejecutar el comando sin la variable de entorno en producción."
        raise EnvironmentError(msg)

    datetime_now = datetime.now()
    if time_end is None:
        time_end = datetime_now
    if isinstance(time_end, timedelta):
        date_end = datetime_now + time_end
    elif isinstance(time_end, datetime):
        date_end = time_end
    else:
        raise ValueError("No se ha establecido la fecha de fin '--date-end'.")

    if time_start is None:
        time_start = date_end.replace(hour=0, minute=0, second=0, microsecond=0)
    if isinstance(time_start, timedelta):
        date_start = date_end + time_start
    elif isinstance(time_start, datetime):
        date_start = time_start
    else:
        raise ValueError("No se ha establecido la fecha de inicio '--date-start'.")

    payload = purchase_order.DataApiPayload("AM", date_start, date_end)
    purchase_order.create_from_service(payload, store, env)

@click.group()
def run():
    """Ejecutar catacteristicas de la integración."""

run.add_command(run_purchase_orders)
