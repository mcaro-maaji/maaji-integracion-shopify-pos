"""
Modulo para hacer login en los sitios web principales de la integración.

- Shopify Plus, Admin
- Stocky
"""

from os import environ
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from .webdriver import BrowserDriver, WebDriverWaitTimeOuted as Wait
from ..config import Configuration, KeySitesShopifyStores
from ..utils import (UrlParser, function_for_test, wait_changes_file,
                     CURRENT_WORKING_DIR, load_dotenv)

@function_for_test
def login_shopify_resolve_segurity_tfa(driver: BrowserDriver, /, timeout=30) -> None:
    """
    Asistente para resolver la autenticación de 2 factores, solo en cuentas Shopify con esta medida 
    de seguridad. En ambiente productivo no será necesaria la función, solo es para pruebas.
    """
    try:
        until = EC.visibility_of_element_located((By.ID, "account_tfa_code"))
        input_tfa_code = Wait(driver, 10).until(until) # 10 segundos de timeout
    except TimeoutException:
        return None # no hay seguridad de dos factores.

    wait_changes_file(CURRENT_WORKING_DIR / ".env", timeout=timeout)
    environ.pop("SHOPIFY_TFA_CODE")
    load_dotenv(CURRENT_WORKING_DIR / ".env")

    input_tfa_code.send_keys(environ.get("SHOPIFY_TFA_CODE") or "")
    commit_botton = Wait(driver).until(EC.element_to_be_clickable((By.NAME, "commit")))
    commit_botton.click()
    return None

@function_for_test
def login_shopify_resolve_segurity_hcaptcha(driver: BrowserDriver) -> float:
    """
    Asistente para resolver la autenticación H-CAPTCHAT, esto evita que la integración
    prosiga con un login al tener esta medida de seguridad.
    """
    try:
        # 10 segundos de timeout.
        Wait(driver, 10).until(EC.visibility_of_element_located((By.ID, "h-captcha")))
    except TimeoutException:
        # 300 segundos (5 minutos) para resolver el captcha
        return 300
    raise WebDriverException("No se puede proseguir, existe la seguridad H-Captcha en la web.")


def is_on_shopify_login(driver: BrowserDriver) -> bool:
    """Comprueba si el navegador está en el sitio de shopify login."""
    return Configuration.sites.is_site("shopify_login", driver.current_url)

def is_on_shopify_admin(driver: BrowserDriver) -> bool:
    """Comprueba si el navegador está en el sitio de shopify admin."""
    return Configuration.sites.is_site("shopify_admin", driver.current_url)

def is_on_stocky(driver: BrowserDriver) -> bool:
    """Comprueba si el navegador está en el sitio de stocky."""
    return Configuration.sites.is_site("stocky", driver.current_url)

def is_on_stocky_login(driver: BrowserDriver) -> bool:
    """Comprueba si el navegador está en el sitio de stocky login."""
    return Configuration.get_site("stocky", "login").geturl() == driver.current_url

def login_shopify_admin_lookup(driver: BrowserDriver) -> None:
    """Inicia sesion desde cero, con usuario y contraseña."""
    shopify_email = environ.get("SHOPIFY_EMAIL")
    shopify_password = environ.get("SHOPIFY_PASSWORD")

    if shopify_email is None or shopify_password is None:
        msg = "No se han establecido credenciales para iniciar sesion en shopify admin."
        raise WebDriverException(msg)

    def commit_botton():
        return Wait(driver).until(EC.element_to_be_clickable((By.NAME, "commit")))

    input_email = Wait(driver).until(EC.visibility_of_element_located((By.ID, "account_email")))
    input_email.send_keys(shopify_email)
    commit_botton().click()

    try:
        timeout_resolve_captcha = login_shopify_resolve_segurity_hcaptcha(driver)
    except EnvironmentError:
        timeout_resolve_captcha = None

    # La seguridad H-Captcha aparece antes del input de la contraseña, por lo tanto
    # se inserta el tiempo de espera en este WaitWebDriver.
    wait_input_password = Wait(driver, timeout_resolve_captcha)

    input_until = EC.visibility_of_element_located((By.ID, "account_password"))
    input_password = wait_input_password.until(input_until)
    input_password.send_keys(shopify_password)
    commit_botton().click()

    try:
        # 180 segundos = 3 minutos, para resolver la seguridad de dos factores
        login_shopify_resolve_segurity_tfa(driver, 180)
    except EnvironmentError:
        pass

def login_shopify_admin_select(driver: BrowserDriver) -> None:
    """Inicia sesión con la cuenta guardada en el login."""
    shopify_email = environ.get("SHOPIFY_EMAIL")
    selected_account = driver.find_element(By.PARTIAL_LINK_TEXT, shopify_email)
    selected_account.click()

def login_shopify_admin(driver: BrowserDriver) -> None:
    """Intenta hacer login en Shopify Admin."""
    if is_on_shopify_admin(driver):
        return None
    driver.get(Configuration.sites.shopify_admin)
    if is_on_shopify_admin(driver):
        return None
    url_login = Configuration.get_site("shopify_login", "store_login")
    driver.get(url_login.geturl())

    if not is_on_shopify_login(driver):
        msg = f"No se ha podido iniciar sesion en Shopify: '{Configuration.sites.shopify_login}'"
        raise WebDriverException(msg)

    url_lookup = Configuration.get_site("shopify_login", "lookup_rid")
    url_select = Configuration.get_site("shopify_login", "select_rid")

    current_url = UrlParser(driver.current_url)
    if current_url.path == url_select.path:
        login_shopify_admin_select(driver)
    elif current_url.path == url_lookup.path:
        login_shopify_admin_lookup(driver)
    else:
        raise WebDriverException("Modelo de login en Shopify no soportado.")


def login_stocky(
                 driver: BrowserDriver,
                 store_key: KeySitesShopifyStores,
                 *,
                 shopify=False) -> None:
    """
    Intenta hacer login en Stocky con la tienda seleccionada.

    :params driver: Se trata del controlador del navegador.
    :type driver: BrowserDriver
    :params store_key: Consiste en la llave que identifica la tienda para iniciar sesión.
    :type store_key: KeySitesShopifyStores
    :params shopify: Fuerza el login en Shopify Plus.
    :type shopify: bool = False
    """
    if shopify:
        login_shopify_admin(driver)

    if not is_on_stocky(driver):
        driver.get(Configuration.sites.stocky)

    store_url = Configuration.get_site("shopify_store:" + store_key)
    try:
        driver.find_element(By.PARTIAL_LINK_TEXT, store_url.netloc)
        return None
    except NoSuchElementException:
        pass

    driver.get(Configuration.get_site("stocky", "login").geturl())

    if not is_on_stocky_login(driver):
        msg = f"No se ha podido iniciar sesion en Stocky: '{Configuration.sites.shopify_login}'"
        raise WebDriverException(msg)

    input_shop = Wait(driver).until(EC.visibility_of_element_located((By.ID, "shop")))
    input_shop.send_keys(store_url.netloc)
    submit_button = Wait(driver).until(EC.element_to_be_clickable((By.TAG_NAME, "button")))
    submit_button.click()
