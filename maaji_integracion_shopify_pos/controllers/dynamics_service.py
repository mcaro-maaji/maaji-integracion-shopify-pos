"""TODO: DOCS"""

from datetime import datetime
from .locations import get_weblocations
# from .stocky import WebStocky, ApiStockySuppliers ### En caso de que proveedor deje ser ART MODE.
from ..data import (dynamics_service as Dynamics, DataPurchaseOrderItemsFile,
                    DataPurchaseOrdersFile, DataLocation)
from ..fieldsmapping import FieldMapping
from ..config import KeySitesShopifyStores

def bill_line_to_purchase_item(bill: Dynamics.DataApiServiceBills, /):
    """
    Convierte un resultado de la factura del servicio dynamics 365 a un item de una
    orden de compra en stocky.
    """
    cantidad = round(float(bill.cantidad))
    costo_compra = bill.costo_compra.replace(",", "")
    return DataPurchaseOrderItemsFile(
        bar_code=bill.ean,
        quantity=cantidad,
        cost_price=costo_compra
    )

def validate_bill_store(bill: Dynamics.DataApiServiceBills, store_key: KeySitesShopifyStores, /):
    """Realiza la validación de la tienda y homologa el campo con la localización el shopify."""
    web_locations = get_weblocations()
    web_locations.update_from_last_updated_at()

    fieldmapping_stores = FieldMapping.stores.find(lambda fd: bill.tienda in fd.codes \
                                                   or bill.tienda in fd.names)
    store_names = None if not fieldmapping_stores.shopify else fieldmapping_stores.shopify[0].names

    err_msg = "No se encontro el campo Tienda de la factura D365 '{}' en Shopify localización: '{}'"
    err = ValueError(err_msg.format(bill.numero_factura, bill.tienda))

    if store_names:
        locations: list[DataLocation] = getattr(web_locations.data, store_key)
        location = next((location for location in locations if location.name in store_names), None)
    else:
        raise err

    if not location:
        raise err
    return location

def validate_bill_supplier(bill: Dynamics.DataApiServiceBills, /):
    """Comprueba el proveedor en Stocky."""
    if bill.proveedor != "900911000":
        msg = f"En la factura '{bill.numero_factura}' proveedor siempre debe ser 'ART MODE'"
        raise ValueError(msg)
    return "ART MODE"

def one_bill_line_to_purchase_order(bill: Dynamics.DataApiServiceBills,
                                    store_key: KeySitesShopifyStores, /):
    """
    Convierte un resultado de la factura del servicio dynamics 365 a una orden de compra en stocky.
    """
    tienda = validate_bill_store(bill, store_key)
    # tienda = 72046280749 # bill.tienda <- ID localizacion Shopify = MAAJI MAYORCA Test
    proveedor = validate_bill_supplier(bill)
    fecha_factura = datetime.strptime(bill.fecha_factura, "%m/%d/%Y").date()

    return DataPurchaseOrdersFile(
        invoice_number=bill.numero_factura,
        invoice_date=fecha_factura,
        currency=bill.moneda,
        shopify_store_key_name=store_key,
        shopify_receive_location_id=tienda.id,
        supplier_name=proveedor
    )

def splitlines_bills(bills: list[Dynamics.DataApiServiceBills], /):
    """Ordena cada linea de las facturas de D365 por numero de factura y separa por cada factura."""
    bills_sorted = sorted(bills, key=lambda bill: bill.numero_factura)
    bills_sorted = filter(lambda bill: bill.numero_factura.startswith("FEV"), bills_sorted)
    bills_lines_splited: list[list[Dynamics.DataApiServiceBills]] = []
    bill_temp: list[Dynamics.DataApiServiceBills] = []

    for bill in bills_sorted:
        if bill_temp and bill_temp[0].numero_factura != bill.numero_factura:
            bills_lines_splited.append(bill_temp)
            bill_temp = []
        bill_temp.append(bill)
    bills_lines_splited.append(bill_temp)
    return bills_lines_splited

def bill_lines_to_purchase_items(bills: list[Dynamics.DataApiServiceBills], /):
    """
    Convierte varios resultado de la factura del servicio dynamics 365 en los articulos (items)
    de una orden de compra en stocky.
    """
    return [bill_line_to_purchase_item(bill) for bill in bills]

def bill_to_purchase_order(bills: list[Dynamics.DataApiServiceBills],
                            store_key: KeySitesShopifyStores, /):
    """
    Convierte varios resultados de la factura del servicio dynamics 365 a una orden de compra
    en stocky.
    """
    if not bills:
        raise ValueError("No hay factura del servicio D365.")

    purchase_items = bill_lines_to_purchase_items(bills)
    row_purchase_order = one_bill_line_to_purchase_order(bills[0], store_key)
    row_purchase_order.purchase_items = purchase_items
    row_purchase_order.amount_paid = sum((float(i.cost_price) * i.quantity for i in purchase_items))
    purchase_order = DataPurchaseOrdersFile()
    purchase_order.__csv_rows__.append(row_purchase_order)
    purchase_order.setrow()
    return purchase_order

def bills_to_purchase_orders(bills: list[Dynamics.DataApiServiceBills],
                            store_key: KeySitesShopifyStores, /):
    """
    Convierte todas las facturas del servicio dynamics 365 a varias ordenes de compra
    en stocky.
    """
    bills_lines_splited = splitlines_bills(bills)
    purchase_orders: list[DataPurchaseOrdersFile] = []
    for bill in bills_lines_splited:
        try:
            purchase_order = bill_to_purchase_order(bill, store_key)
            purchase_orders.append(purchase_order)
        except ValueError: # No se homologa el campo Tienda con la localizacion en shopify
            pass
    return purchase_orders
