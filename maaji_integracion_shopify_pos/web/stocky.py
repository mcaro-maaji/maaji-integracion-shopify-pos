"""TODO: DOCS"""

from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from .webdriver import BrowserDriver, WebDriverWaitTimeOuted as Wait
from .login import login_shopify_admin, is_on_shopify_admin, login_stocky
from ..config import Configuration, key_sites_shopify_stores, KeySitesShopifyStores
from ..data import DataStocky, DataStockyFile

class WebStockyFile:
    """Manejador Web de información básica de stocky junto al archivo JSON."""
    def __init__(self, driver: BrowserDriver, data: DataStockyFile, /) -> None:
        self.driver = driver
        self.data = data

    def get_api_key(self, store_key: KeySitesShopifyStores, /) -> None:
        """
        Halla la api keys de stocky de la tienda seleccionada.

        Nota: Se requiere haber iniciado sesion en el sitio Shopify Admin.
        """
        url = Configuration.get_site("stocky", "select_api")
        self.driver.get(url.geturl())

        try:
            element_api_key = self.driver.find_element(By.TAG_NAME, "code")
        except NoSuchElementException:
            css_selector = "a[href^=\"/accounts/create_api_key\"]"
            until = EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            try:
                Wait(self.driver).until(until).click()
                element_api_key = self.driver.find_element(By.TAG_NAME, "code")
            except (NoSuchElementException, TimeoutException) as err:
                err.msg = "No se ha encontrado el elemento para obtener la api key de stocky."
                raise err

        base_stocky: DataStocky = getattr(self.data, store_key)
        base_stocky.api_key = element_api_key.text

    def update(self) -> None:
        """Actualiza la data de información básica de stocky de las tiendas."""
        current_url = self.driver.current_url

        login_shopify_admin(self.driver)
        if not is_on_shopify_admin(self.driver):
            return None

        for store_key in key_sites_shopify_stores:
            try:
                login_stocky(self.driver, store_key)
            except WebDriverException:
                continue
            self.get_api_key(store_key)

        self.driver.get(current_url)
        self.data.save_file()
        return None

    def update_from_last_updated_at(self, range_time=timedelta(days=1)) -> None:
        """
        Actualiza información básica de stocky solo si desde la ultima actualización no ha pasado
        el rango de tiempo dado en el parametro *range_time*.

        Por defecto, desde el ultimo día de actualización.
        """
        updated_at = self.data.__metadata__.updated_at
        if updated_at is None:
            self.update()
        else:
            diference_updated = datetime.now() - updated_at
            if diference_updated > range_time:
                self.update()
