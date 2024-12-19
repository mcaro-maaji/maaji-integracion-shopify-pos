"""TODO: DOCS"""

from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import JavascriptException, WebDriverException
from .webdriver import BrowserDriver, WebDriverWaitTimeOuted as Wait
from .login import login_shopify_admin, is_on_shopify_admin, login_stocky
from ..config import Configuration, key_sites_shopify_stores, KeySitesShopifyStores
from ..data import DataLocation, DataLocationsFile

class WebLocationsFile:
    """Manejador Web de las localizaciones y el archivo JSON."""
    def __init__(self, driver: BrowserDriver, data: DataLocationsFile, /) -> None:
        self.driver = driver
        self.data = data

    def get_locations(self, store_key: KeySitesShopifyStores, /) -> None:
        """
        Halla todas las localizaciones de la tienda seleccionada.

        Nota: Se requiere haber iniciado sesion en el sitio Shopify Admin.
        """
        store = store_key.replace("_", "-")
        url = Configuration.get_site("shopify_admin", "select_locations", shopify_store=store)
        self.driver.get(url.geturl())

        locator = (By.CSS_SELECTOR, "body div[hidden=true]")
        Wait(self.driver).until(EC.presence_of_element_located(locator))

        try:
            script = "return JSON.parse(document.body.firstChild.innerText);"
            json_data = self.driver.execute_script(script)
            locations = [DataLocation.from_dict(item) for item in json_data["locations"]]
        except JavascriptException as err:
            msg = f"Error al analizar el JSON de las localizaciones de la tienda: '{store_key}'"
            raise WebDriverException(msg) from err

        setattr(self.data, store_key, locations)

    def set_stocky_id(self, store_key: KeySitesShopifyStores, /) -> None:
        """
        Halla el id stocky para todas las localizaciones de la tienda seleccionada.

        Nota: Se requiere haber iniciado sesion en el sitio Shopify Admin.
        """
        url_locations = Configuration.get_site("stocky", "select_locations").geturl()
        self.driver.get(url_locations)

        anchor_locations = self.driver.find_elements(By.CSS_SELECTOR, "a[href^=\"/locations/\"]")
        locations: list[DataLocation] = getattr(self.data, store_key)

        for index_location, location in enumerate(locations):
            index = next((idx for idx, anchor_location in enumerate(anchor_locations)
                          if anchor_location.text == location.name), -1)
            if index == -1:
                continue
            anchor_location = anchor_locations[index]
            # href=/locations/[123123] <-- ID Stocky DataLocation
            stocky_id = anchor_location.get_attribute("href").split("/")[-1]
            if isinstance(stocky_id, str) and stocky_id.isdecimal():
                locations[index_location].stocky_id = int(stocky_id)
        setattr(self.data, store_key, locations)

    def update(self) -> None:
        """Actualiza la data de las localizaciones de las tiendas."""
        current_url = self.driver.current_url

        login_shopify_admin(self.driver)
        if not is_on_shopify_admin(self.driver):
            return None

        for store_key in key_sites_shopify_stores:
            self.get_locations(store_key)
            try:
                login_stocky(self.driver, store_key)
            except WebDriverException:
                continue
            self.set_stocky_id(store_key)

        self.driver.get(current_url)
        self.data.save_file()
        return None

    def update_from_last_updated_at(self, range_time=timedelta(days=1)) -> None:
        """
        Actualiza las localizaciones solo si desde la ultima actualización no ha pasado el rango de
        tiempo dado en el parametro *range_time*.

        Por defecto, desde el ultimo día de actualización.
        """
        updated_at = self.data.__metadata__.updated_at
        if updated_at is None:
            self.update()
        else:
            diference_updated = datetime.now() - updated_at
            if diference_updated > range_time:
                self.update()
