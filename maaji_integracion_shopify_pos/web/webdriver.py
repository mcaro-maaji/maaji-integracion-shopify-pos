"""TODO: DOCS"""

from typing import Literal, Type
from functools import lru_cache
from pathlib import Path
from selenium.types import WaitExcTypes
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import POLL_FREQUENCY
from selenium.webdriver import (Chrome, ChromeOptions, ChromeService,
                                Edge, EdgeOptions, EdgeService,
                                Firefox, FirefoxOptions, FirefoxService)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from ..config import Configuration
from ..utils import ENVIRONMENT, WORKING_DIR

BrowserAlias   = Literal["chrome", "edge", "firefox"]
BrowserDriver  = Chrome        | Edge        | Firefox
BrowserService = ChromeService | EdgeService | FirefoxService
BrowserOptions = ChromeOptions | EdgeOptions | FirefoxOptions

class WebDriverWaitTimeOuted(WebDriverWait):
    """Clase que se establece un tiempo de espera predefinido en la configuracion."""

    def __init__(self,
                 driver: WebDriver,
                 timeout: float | None = None,
                 poll_frequency: float = POLL_FREQUENCY,
                 ignored_exceptions: WaitExcTypes | None = None) -> None:
        if timeout is None:
            timeout = Configuration.webdriver.wait_timeout or 10
        super().__init__(driver, timeout, poll_frequency, ignored_exceptions)


def check_webdriver_available(webdriver_type: BrowserAlias):
    """Función para verificar si el WebDriver correspondiente está disponible."""
    if webdriver_type == "chrome":
        return Path(ChromeDriverManager().install()).exists()
    if webdriver_type == "edge":
        return Path(EdgeChromiumDriverManager().install()).exists()
    if webdriver_type == "firefox":
        return Path(GeckoDriverManager().install()).exists()
    return False

@lru_cache(maxsize=None)
def get_webdriver_params(name: BrowserAlias) -> tuple[Type[BrowserDriver],
                                                      BrowserService, BrowserOptions]:
    """Obtener los parametors (controlador, servicio, opciones) del navegador según el nombre."""
    is_available_webdriver = check_webdriver_available(name)

    if is_available_webdriver and name == "chrome":
        driver = Chrome
        service = ChromeService(ChromeDriverManager().install())
        options = ChromeOptions()
    elif is_available_webdriver and name == "edge":
        driver = Edge
        service = EdgeService(EdgeChromiumDriverManager().install())
        options = EdgeOptions()
    elif is_available_webdriver and name == "firefox":
        driver = Firefox
        service = FirefoxService(GeckoDriverManager().install())
        options = FirefoxOptions()
    else:
        raise WebDriverException("No se encontró un WebDriver disponible.")

    return (driver, service, options)

def get_dir_webdriver(profile: str | None = None, name: BrowserAlias | None = None) -> Path:
    """Devuelve el Path del directorio de datos de usuario en el navegador."""
    env = ENVIRONMENT
    profile = profile or Configuration.webdriver.profile or "profile_default"
    folder_profile = "_".join([env, name, profile]) # /prod_edge_profile_default
    path = WORKING_DIR / f"webdriver_profiles/{folder_profile}"
    return path

@lru_cache(maxsize=None)
def get_webdriver(profile: str | None = None, name: BrowserAlias | None = None) -> BrowserDriver:
    """Obtener el controlador del navegador, función memo."""
    if not name:
        name_webdriver = Configuration.webdriver.name_webdriver
        if name_webdriver.lower() in ("chrome", "edge", "firefox"):
            name = name_webdriver
        else:
            name = "chrome"
    [webdriver, service, options] = get_webdriver_params(name)

    option_arguments = Configuration.webdriver.options.add_arguments
    if option_arguments:
        for argument in option_arguments:
            options.add_argument(argument)

    user_data_dir = get_dir_webdriver(profile, name).absolute().as_posix()
    options.add_argument(f"user-data-dir={user_data_dir}")

    return webdriver(options, service)
