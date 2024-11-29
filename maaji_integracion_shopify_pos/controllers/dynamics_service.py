"""TODO: DOCS"""

from datetime import datetime
from .locations import WebLocations
# from .stocky import WebStocky, ApiStockySuppliers ### En caso de que proveedor deje ser ART MODE.
from ..data import (dynamics_service as Dynamics, DataPurchaseOrderItemsFile,
                    DataPurchaseOrdersFile, DataLocation)
from ..fieldsmapping import FieldMapping
from ..config import KeySitesShopifyStores

def bill_to_purchase_item(bill: Dynamics.DataApiServiceBills, /):
    """
    Convierte un resultado de la factura del servicio dynamics 365 a un item de una
    orden de compra en stocky.
    """
    cantidad = int(float(bill.cantidad))
    costo_compra = bill.costo_compra.replace(",", "")
    return DataPurchaseOrderItemsFile(
        bar_code=bill.ean,
        quantity=cantidad,
        cost_price=costo_compra
    )

def validate_bill_store(bill: Dynamics.DataApiServiceBills, store_key: KeySitesShopifyStores, /):
    """Realiza la validación de la tienda y homologa el campo con la localización el shopify."""
    WebLocations.update_from_last_updated_at()

    fieldmapping_stores = FieldMapping.stores.find_by(lambda fd: bill.tienda in fd.codes)
    store_names = None if not fieldmapping_stores.shopify else fieldmapping_stores.shopify[0].names

    err_msg = "No se homologó el campo Tienda de la factura D365 '{}' con Shopify localización."
    err = ValueError(err_msg.format(bill.numero_factura))

    if store_names:
        locations: list[DataLocation] = getattr(WebLocations.data, store_key)
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
    return "ART MODE S.A.S BIC"

def bill_to_purchase_order(bill: Dynamics.DataApiServiceBills, store_key: KeySitesShopifyStores, /):
    """
    Convierte un resultado de la factura del servicio dynamics 365 a una orden de compra en stocky.
    """
    # tienda = validate_bill_store(bill, store_key)
    tienda = 72046280749 # bill.tienda = CE600 <- ID localizacion Shopify = MAAJI MAYORCA
    proveedor = validate_bill_supplier(bill)
    fecha_factura = datetime.strptime(bill.fecha_factura, "%d/%m/%Y").date()

    return DataPurchaseOrdersFile(
        invoice_number=bill.numero_factura,
        invoice_date=fecha_factura,
        currency=bill.moneda,
        shopify_store_key_name=store_key,
        shopify_receive_location_id=tienda,
        supplier_name=proveedor
    )

def split_bills(bills: list[Dynamics.DataApiServiceBills], /):
    """Ordena cada linea de las facturas de D365 por numero de factura y separa por cada factura."""
    bills_sorted = sorted(bills, key=lambda bill: bill.numero_factura)
    bills_splited: list[list[Dynamics.DataApiServiceBills]] = []
    bills_temp: list[Dynamics.DataApiServiceBills] = []

    for bill in bills_sorted:
        if bills_temp and bills_temp[0].numero_factura != bill.numero_factura:
            bills_splited.append(bills_temp)
            bills_temp = []
        bills_temp.append(bill)
    return bills_splited

def bill_to_purchase_items(bills: list[Dynamics.DataApiServiceBills], /):
    """
    Convierte varios resultado de la factura del servicio dynamics 365 en los articulos (items)
    de una orden de compra en stocky.
    """
    return [bill_to_purchase_item(bill) for bill in bills]

def bills_to_purchase_order(bills: list[Dynamics.DataApiServiceBills],
                            store_key: KeySitesShopifyStores, /):
    """
    Convierte varios resultados de la factura del servicio dynamics 365 a una orden de compra
    en stocky.
    """
    if not bills:
        raise ValueError("No hay factura del servicio D365.")

    purchase_order = bill_to_purchase_order(bills[0], store_key)
    purchase_items = bill_to_purchase_items(bills)
    purchase_order.purchase_items = purchase_items
    return purchase_order

def bills_to_purchase_orders(bills: list[Dynamics.DataApiServiceBills],
                            store_key: KeySitesShopifyStores, /):
    """
    Convierte todas las facturas del servicio dynamics 365 a varias ordenes de compra
    en stocky.
    """
    return [bills_to_purchase_order(bill_splited, store_key) for bill_splited in split_bills(bills)]
