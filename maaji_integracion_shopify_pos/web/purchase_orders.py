"""TODO: DOCS"""

from urllib.parse import urlparse
from datetime import date, datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from .webdriver import BrowserDriver, WebDriverWaitTimeOuted as Wait
from .login import login_stocky
from .stocky import WebStockyFile
from .locations import WebLocationsFile
from ..api.stocky import ApiStockyFile
from ..data.dataclass import EnumMetaDataFileStatus
from ..data import DataPurchaseOrdersFile, DataLocation, DataSupplier
from ..config import Configuration, key_sites_shopify_stores, KeySitesShopifyStores

class WebPurchaseOrderFile:
    """Manejador Web de las ordenes de compra en Stocky, usando archivos CSV."""
    def __init__(self,
                 driver: BrowserDriver,
                 web_locations: WebLocationsFile,
                 web_stocky: WebStockyFile,
                 api_suppliers: ApiStockyFile,
                 data: DataPurchaseOrdersFile,
                 /) -> None:
        self.driver = driver
        self.web_locations = web_locations
        self.web_stocky = web_stocky
        self.api_suppliers = api_suppliers
        self.data = data
        self.key_store = data.shopify_store_key_name

    def validate_location(self) -> tuple[KeySitesShopifyStores, DataLocation]:
        """Comprueba la localización de la orden de compra."""
        if self.data.shopify_receive_location_id is None:
            raise ValueError("No se ha establecido una localización a la orden de compra.")

        location_id = self.data.shopify_receive_location_id
        self.web_locations.update_from_last_updated_at()

        for key_store in key_sites_shopify_stores:
            locations: list[DataLocation] = getattr(self.web_locations.data, key_store)
            index = next((idx for idx, location in enumerate(locations)
                          if location.id == location_id), -1)
            if index != -1:
                self.data.shopify_store_key_name = key_store
                self.key_store = key_store
                return (key_store, locations[index])
        raise ValueError("No se ha establecido una localización correcta o no hay localizaciones.")

    def validate_key_store(self) -> KeySitesShopifyStores:
        """Comprueba que el nombre de la tienda sea correcto."""
        if self.key_store is not None and self.key_store in key_sites_shopify_stores:
            return self.key_store
        raise ValueError("No se ha seleccionado una tienda valida.")

    def validate_supplier(self) -> DataSupplier:
        """Comprueba que el proveedor exista en Stocky."""
        supplier_id = self.data.supplier_id
        supplier_name = self.data.supplier_name
        key_store = self.validate_key_store()

        if not supplier_id and not supplier_name:
            raise ValueError("No se ha encontrado un proveedor en la orden de compra.")

        self.web_stocky.update_from_last_updated_at()
        self.api_suppliers.update_from_last_updated_at()
        suppliers: list[DataSupplier] = getattr(self.api_suppliers.service, key_store)
        index = -1

        for idx, supplier in enumerate(suppliers):
            if (supplier_id is not None and supplier.id == supplier_id) \
                or supplier.name == supplier_name:
                if suppliers[idx].is_hidden is not None and suppliers[idx].is_hidden:
                    continue
                index = idx
            if index != -1:
                break

        if index != -1 and supplier_id:
            self.data.supplier_id = supplier_id
            self.data.supplier_name = suppliers[index].name
        elif supplier_id is None and index != -1 and supplier_name:
            self.data.supplier_name = supplier_name
            self.data.supplier_id = suppliers[index].id
        else:
            raise ValueError("No se ha establecido un proveedor correcto en la orden de compra.")

        return suppliers[index]

    def validate_data_id(self) -> str:
        """Comprueba que el id de la orden de compra existe."""
        if not self.data.id:
            raise ValueError("No se ha establecido un valor id en la orden de compra.")
        return self.data.id

    def validate_exists(self) -> bool:
        """
        Comprueba que existe la orden de compra en Stocky.
        Si existe redirecciona el navegador hacia la orden de compra.
        """
        if not self.data.id:
            return False
        url = Configuration.get_site("stocky", "select_purchase_order", id=self.data.id)
        self.driver.get(url.geturl())
        locator = (By.XPATH, "/html/body/div[1]/div[1]/div/div[1]/div[1]/div/h1")
        until = EC.text_to_be_present_in_element(locator, " Purchase order #")
        try:
            Wait(self.driver).until(until)
            return True
        except TimeoutException:
            return False

    def set_id_data(self) -> None:
        """
        Obtener el id de la orden de compra desde la URL justo despues de haber creado la orden.
        
        ej. "https://stocky.shopifyapps.com/purchase_orders/[7135861]" <-- ID
        
        Nota: Se requiere que el driver se encuentre en el sitio de la orden de compra.
        """
        try:
            self.validate_data_id()
            return None
        except ValueError:
            pass

        Wait(self.driver).until(EC.url_matches(r"/\d+$"))
        url_purchase = urlparse(self.driver.current_url)
        self.data.id = int(url_purchase.path.split("/")[-1])

        # Extraer el número de la orden desde el elemento visible en el DOM en la propiedad "value".
        # Al ser el elemento de tipo <input>, a nivel de interfaz se puede cambiar el número de la
        # orden de compra (ADVERTENCIA de modificaciones).
        # El id del elemento <input> donde está el valor del numero de compra es la frase
        # ("PurchaseOrder" + id de la compra)
        until = EC.visibility_of_element_located((By.ID, f"PurchaseOrder{self.data.id}"))
        input_order_number = Wait(self.driver).until(until)
        self.data.number = int(input_order_number.get_attribute("value"))
        return None

    def new(self) -> None:
        """Via Web crear la orden de compra, valida la localización y el proveedor."""
        if self.validate_exists() or self.data.getstatus() == EnumMetaDataFileStatus.COMPLETED:
            # No crear una nueva orden de compra si ya está en estado completo.
            return None # TODO: Log event

        [key_store, location] = self.validate_location()
        login_stocky(self.driver, key_store, shopify=True)

        url = Configuration.get_site("stocky", "create_purchase_order")
        self.driver.get(url.geturl())

        def dropdown(id_element: str):
            until = EC.visibility_of_element_located((By.ID, id_element))
            return Select(Wait(self.driver).until(until))

        dropdown("vendor_or_supplier").select_by_visible_text("Supplier")
        # Validación de proveedor, por defecto es ART MODE
        supplier_default_name = Configuration.purchase_orders.default_supplier_name_like
        if not supplier_default_name:
            supplier_default_name = "ART MODE S.A.S. BIC"
        if not self.data.supplier_name:
            self.data.supplier_name = supplier_default_name

        supplier = self.validate_supplier()
        dropdown("supplier_id").select_by_value(str(supplier.id))
        # Caracteristica de Stocky sin relevancia # TODO: Revizar que utilidad brinda.
        dropdown("generate").select_by_visible_text("Blank")
        # Validación de la localización de la tienda.
        dropdown("location_id").select_by_value(str(location.stocky_id))
        Wait(self.driver).until(EC.element_to_be_clickable((By.NAME, "commit"))).click()
        self.set_id_data()

    def is_mark_ordered(self) -> bool:
        """Comprueba que la orden de compra esté marcado como ordenado."""
        self.validate_data_id()
        url = Configuration.get_site("stocky", "select_purchase_order", id=self.data.id)
        is_current_purchase = self.driver.current_url == url.geturl()

        if not is_current_purchase and not self.validate_exists():
            raise ValueError("No existe la orden de compra en Stocky.")

        try:
            # valida que anchor receive (boton link de recibir) exista en la orden de compra.
            self.driver.find_element(By.ID, "receive_and_sync")
            return True
        except NoSuchElementException:
            return False

    def add_products(self) -> None:
        """Añadir los productos a una orden de compra."""
        if self.is_mark_ordered():
            return None
        if not self.data.purchase_items:
            raise ValueError("No hay productos por añadir en la orden de compra.")

        url = Configuration.get_site("stocky", "purchase_orders_add_products", id=self.data.id)
        self.driver.get(url.geturl())

        file_until = EC.visibility_of_element_located((By.ID, "purchase_item_import_file_url"))
        input_file = Wait(self.driver).until(file_until)
        path_file = self.data.getpath() / self.data.getname()
        path_file = str(path_file.absolute())
        input_file.send_keys(path_file)

        timeout = Configuration.purchase_orders.timeout_add_products or 300 # 5 minutos
        input_summit_until = EC.element_to_be_clickable((By.NAME, "commit"))
        input_summit = Wait(self.driver, timeout).until(input_summit_until)
        input_summit.click()

        if not self.data.purchase_items[0].bar_code is None:
            identifier_product = "bar_code"
            type_identifier_product = "Barcode"
        elif not self.data.purchase_items[0].sku is None:
            identifier_product = "sku"
            type_identifier_product = "SKU"
        elif not self.data.purchase_items[0].variant_shopify_id is None:
            identifier_product = "variant_shopify_id"
            type_identifier_product = "Shopify Variant ID"
        else:
            identifier_product = None
            type_identifier_product = None

        if identifier_product is None:
            msg = "Se requiere nombre de la columna que identifica al producto [bar_code, sku]"
            raise ValueError(msg)

        context = self.data.getcontext()
        identifier_product = context.purchase_items_fstr.format(identifier_product)

        def dropdown(id_element: str):
            until = EC.visibility_of_element_located((By.ID, id_element))
            return Select(Wait(self.driver).until(until))

        dropdown("indentifier_column").select_by_visible_text(identifier_product)
        dropdown("indentifier_type_column").select_by_visible_text(type_identifier_product)
        quantity_column = context.purchase_items_fstr.format("quantity")
        dropdown("quantity_column").select_by_visible_text(quantity_column)
        cost_column = context.purchase_items_fstr.format("cost_price")
        dropdown("cost_column").select_by_visible_text(cost_column)

        Wait(self.driver).until(EC.element_to_be_clickable((By.NAME, "commit"))).click()


    # FIXME: Arreglar esta caracteristica de añadir el campo ENVIO.
    # def edit_shipping_purchase_order(driver: BrowserDriver, data: DataPurchaseOrder):
    #     if data.id is None: return False
    #     current_url = driver.current_url
    #     shipping_is_none = data.shipping.first_row is None
    #     shipping_tax_type_is_none = data.shipping.first_row is None

    #     if not shipping_is_none or not shipping_tax_type_is_none:
    #         url_update_shipping = BotConfig.get_site_action("shopify_stocky", "purchase_orders_update_shipping", id=data.id).geturl()
    #         driver.get(url_update_shipping)
    #         if not shipping_is_none:
    #         driver.find_element(By.ID, f"purchase_order_shipping").send_keys = data.shipping.first_row
            
    #         shipping_tax_type = data.shipping_tax_type_id.first_row
    #         if shipping_tax_type is not None and shipping_tax_type.isdecimal():
    #         shipping_tax_type = int(shipping_tax_type)
    #         shipping_tax_type = BotConfig.get_tax_type(shipping_tax_type)
    #         else: shipping_tax_type = None

    #         if shipping_tax_type_is_none is not None and shipping_tax_type is not None:
    #         select_tax_type = Select(driver.find_element(By.ID, f"purchase_order_shipping_tax_type"))
    #         select_tax_type.select_by_value=(data.shipping_tax_type_id.first_row)

    #         driver.find_element(By.ID, "commit").click()
    #         driver.get(current_url)
    #         return True
    #     return False

    def fill_form(self):
        """Rellena todo el formulario de datos en la orden de compra."""
        if self.is_mark_ordered():
            return None

        def fill_element(id_element: str, send_keys: str, clear=True):
            element = self.driver.find_element(By.ID, id_element)
            if clear:
                element.clear()
            element.send_keys(str(send_keys))

        if not self.data.amount_paid is None:
            fill_element("total_field_{self.data.id}", str(self.data.amount_paid))

        if not self.data.paid is None:
            input_paid = self.driver.find_element(By.ID, "purchase_order_paid")
            is_paid = self.data.paid
            is_input_paid_select = input_paid.is_selected()
            if (is_paid and not is_input_paid_select) or (not is_paid and is_input_paid_select):
                input_paid.click()

        if not self.data.adjustments is None:
            fill_element("purchase_order_adjustments", str(self.data.adjustments))
        if not self.data.invoice_number is None:
            fill_element("purchase_order_invoice_number", self.data.invoice_number)
        if not self.data.supplier_order is None:
            fill_element("purchase_order_supplier_order_number", self.data.supplier_order)

        def cast_to_date(value: date | datetime | None) -> str | None:
            if isinstance(value, (date, datetime)):
                return value.strftime("%d/%m/%Y")
            return None

        payment_due_on = cast_to_date(self.data.payment_due_on)
        payment_on = cast_to_date(self.data.payment_on)
        ordered_at = cast_to_date(self.data.ordered_at)
        invoice_date = cast_to_date(self.data.invoice_date)
        ship_on = cast_to_date(self.data.ship_on)
        expected_on = cast_to_date(self.data.expected_on)
        cancel_on = cast_to_date(self.data.cancel_on)
        if not payment_due_on is None:
            fill_element("purchase_order_payment_due_on", payment_due_on)
        if not payment_on is None:
            fill_element("purchase_order_paid_on", payment_on)
        if not ordered_at is None:
            fill_element("purchase_order_purchase_order_date", ordered_at)
        if not invoice_date is None:
            fill_element("purchase_order_invoice_date", invoice_date)
        if not ship_on is None:
            fill_element("purchase_order_ship_on", ship_on)
        if not expected_on is None:
            fill_element("purchase_order_expected_on", expected_on)
        if not cancel_on is None:
            fill_element("purchase_order_cancel_on", cancel_on)

    def mark_ordered(self) -> None:
        """Marcar como ordenado la orden de compra."""
        if self.is_mark_ordered():
            return None

        path_url = Configuration.get_site("stocky",
                                          "purchase_orders_mark_ordered",
                                          id=self.data.id).path
        until = EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href=\"{path_url}\"]"))
        anchor_mark_ordered = Wait(self.driver).until(until)
        anchor_mark_ordered.click()
        return None

    def create(self, *, skip_err=False) -> None:
        """
        Crea la orden de compra desde cero, si ya existe añade los productos y rellena
        el formulario y marca como ordenado.
        """
        try:
            self.new()
            self.fill_form()
            self.add_products()
            self.mark_ordered()
        except WebDriverException as err:
            if not skip_err:
                raise err
