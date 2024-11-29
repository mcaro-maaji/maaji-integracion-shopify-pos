"""TODO: DOCS"""

from .dynamics_service import bills_to_purchase_orders
from .locations import WebLocations
from .stocky import WebStocky, ApiStockySuppliers
from ..api.dynamics_service import get_service, DataApiPayload
from ..web.webdriver import get_webdriver
from ..web.purchase_orders import WebPurchaseOrderFile
from ..data import DataPurchaseOrdersFile, FilePurchaseOrderContext
from ..config import KeySitesDynamics, KeySitesShopifyStores
from ..utils import WORKING_DIR

purchase_order_context = FilePurchaseOrderContext()
purchase_order_fieldnames = [None] * len(purchase_order_context.purchase_items_context.onload.fieldnames)
purchase_order_fieldnames.extend(purchase_order_context.onload.fieldnames)
purchase_order_items_fieldnames = list(purchase_order_context.purchase_items_context.onload.fieldnames)
purchase_order_items_fieldnames.extend([None] * len(purchase_order_context.onload.fieldnames))

def create_from_path(path: str, /):
    """Crea una orden de compra desde una ruta."""

    driver = get_webdriver()

    data_purchase_order = DataPurchaseOrdersFile()

    context = FilePurchaseOrderContext()
    context.onload.fieldnames = purchase_order_fieldnames
    context.purchase_items_context.onload.fieldnames = purchase_order_items_fieldnames
    context.onsave.fieldnames = purchase_order_fieldnames
    context.purchase_items_context.onsave.fieldnames = purchase_order_items_fieldnames

    data_purchase_order.setcontext(context)
    data_purchase_order.setpath(path)
    data_purchase_order.load_file(skip_err=False)

    web_purchase_order = WebPurchaseOrderFile(driver, WebLocations, WebStocky,
                                              ApiStockySuppliers, data_purchase_order)
    web_purchase_order.create(skip_err=True)

    driver.close()
    driver.quit()


def create_from_service(payload: DataApiPayload,
                        store_key: KeySitesShopifyStores,
                        dynamics_env: KeySitesDynamics,
                        /):
    """Crear ordenes de compra en stocky mediante el servicio de D365."""
    driver = get_webdriver()
    bills = get_service("bills", payload, dynamics_env)
    purchase_orders = bills_to_purchase_orders(bills, store_key)
    context = FilePurchaseOrderContext()
    context.onload.fieldnames = purchase_order_fieldnames
    context.purchase_items_context.onload.fieldnames = purchase_order_items_fieldnames
    context.onsave.fieldnames = purchase_order_fieldnames
    context.purchase_items_context.onsave.fieldnames = purchase_order_items_fieldnames
    path_purchase = WORKING_DIR / "pedido_de_compra/Almacenamiento/"
    path_purchase.chmod(0o777)
    for purchase_order in purchase_orders:
        web_purchase_order = WebPurchaseOrderFile(driver, WebLocations, WebStocky,
                                                  ApiStockySuppliers, purchase_order)
        web_purchase_order.data.setcontext(context)
        web_purchase_order.data.setpath(path_purchase)
        web_purchase_order.data.save_file()
        web_purchase_order.create(skip_err=False)
        web_purchase_order.data.save_file()
