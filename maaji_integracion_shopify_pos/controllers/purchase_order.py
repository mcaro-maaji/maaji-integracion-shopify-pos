"""TODO: DOCS"""

from datetime import datetime
from selenium.common.exceptions import WebDriverException
from .dynamics_service import bills_to_purchase_orders
from .locations import WebLocations
from .stocky import WebStocky, ApiStockySuppliers
from ..api.dynamics_service import get_service, DataApiPayload
from ..web.webdriver import get_webdriver
from ..web.purchase_orders import WebPurchaseOrderFile
from ..data.dataclass import EnumMetaDataFileStatus as FileStatus
from ..data import DataPurchaseOrdersFile, FilePurchaseOrderContext
from ..config import KeySitesDynamics, KeySitesShopifyStores
from ..utils import WORKING_DIR

PURCHASE_DIR = WORKING_DIR / "pedido_de_compra"

default_context = FilePurchaseOrderContext()
default_fieldnames = ['id',	'number', 'invoice_number', 'supplier_name', 'supplier_id',
                      'currency', 'shopify_receive_location_id', 'invoice_date',
                      'shopify_store_key_name']
default_items_fieldnames = ['bar_code', 'quantity', 'cost_price']
default_items_fieldnames.extend([None] * len(default_fieldnames))
default_fieldnames = [None, None, None, *default_fieldnames]

def create_from_path(path: str, /):
    """Crea una orden de compra desde una ruta."""

    driver = get_webdriver()

    data_purchase_order = DataPurchaseOrdersFile()

    context = FilePurchaseOrderContext()
    context.onload.fieldnames = default_fieldnames
    context.purchase_items_context.onload.fieldnames = default_items_fieldnames
    context.onsave.fieldnames = default_fieldnames
    context.purchase_items_context.onsave.fieldnames = default_items_fieldnames

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
    data_purchase_orders = bills_to_purchase_orders(bills, store_key)
    context = FilePurchaseOrderContext()
    context.onload.fieldnames = default_fieldnames
    context.purchase_items_context.onload.fieldnames = default_items_fieldnames
    context.onsave.fieldnames = default_fieldnames
    context.purchase_items_context.onsave.fieldnames = default_items_fieldnames

    for data_purchase_order in data_purchase_orders:
        web_purchase_order = WebPurchaseOrderFile(driver, WebLocations, WebStocky,
                                                  ApiStockySuppliers, data_purchase_order)
        data_purchase_order.setcontext(context)
        date_str = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        name = f'Compra {data_purchase_order.invoice_number} {date_str}.csv'
        data_purchase_order.setname(name)
        data_purchase_order.setpath(PURCHASE_DIR / "Entrada", FileStatus.ON_HOLD)
        data_purchase_order.setpath(PURCHASE_DIR / "Almacenamiento", FileStatus.COMPLETED)
        data_purchase_order.setpath(PURCHASE_DIR / "Rechazado", FileStatus.ON_REJECT)
        status = FileStatus.ON_HOLD
        data_purchase_order.setstatus(status)
        data_purchase_order.save_file()
        try:
            web_purchase_order.create(skip_err=False)
            status = FileStatus.COMPLETED
        except WebDriverException:
            status = FileStatus.ON_REJECT
        data_purchase_order.flush_row()
        data_purchase_order.save_file()
        data_purchase_order.move_file(status)