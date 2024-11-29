"""
Este archivo brinda utilidades básicas para todo el proyecto.
"""

import time
from typing import Protocol, TypeVar, Generic, Any
from os import environ
from pathlib import Path
from functools import wraps
from urllib.parse import ParseResult as AbsUrlParseResult, urlparse, urlunparse
from dotenv import load_dotenv as __load_dotenv

# Imports solo para entorno de desarrollo (para pruebas):
try:
    from watchdog.observers import Observer as WatchDogObserver
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent
except ImportError:
    WatchDogObserver = None
    FileSystemEventHandler = None

T = TypeVar("T")

NAME_PROYECT = "Maaji Integracion Shopify POS"
ROOT_DIR = Path(__file__).parent
CURRENT_WORKING_DIR = Path.cwd()
DEFAULT_WORKING_DIR = Path.home() / (".data-" + NAME_PROYECT.replace(" ", "-"))
__KEY_ENV_WORKING_DIR = "WORKING_DIR_" + NAME_PROYECT.replace(" ", "_").upper()
WORKING_DIR = Path(environ.get(__KEY_ENV_WORKING_DIR) or DEFAULT_WORKING_DIR)
ENVIRONMENT = "prod" if environ.get("ENVIRONMENT", "").lower() == "production" else "dev"

def __create_data_dir(path: Path, /) -> None:
    return path.mkdir(mode=511, parents=True, exist_ok=True)


if not WORKING_DIR.exists():
    __create_data_dir(WORKING_DIR)
elif not WORKING_DIR.is_dir():
    __create_data_dir(DEFAULT_WORKING_DIR)
    WORKING_DIR = DEFAULT_WORKING_DIR


def load_dotenv(dotenv_path=WORKING_DIR / ".env", / , override=False):
    """Cargar las variables de entorno."""

    if ENVIRONMENT == "prod":
        override = False
    return __load_dotenv(dotenv_path, override=override)


class UrlParser(AbsUrlParseResult):
    """
    Clase para mejorar el uso de las URL.

    Caso de Uso
    ___________
    Operador de división: Concatenar los Paths de las URL.
    
    >>> url1 = UrlParser("https://mi_web.com/path1/data")
    >>> url2 = UrlParser("https://other_web.com/path2/file.csv")
    >>> url3 = url1 / url2
    >>> url1
     UrlParser(scheme='https', netloc='mi_web.com'. path='/path1/data/')
    >>> url3
     UrlParser(scheme='https', netloc='mi_web.com'. path='/path1/data/path2/file.csv')
    """
    def __new__(cls, url_str: str, /):
        url = urlparse(url_str.removesuffix("/"))
        return super().__new__(
            cls,
            url.scheme,
            url.netloc,
            url.path,
            url.params,
            url.query,
            url.fragment
        )

    def __init__(self, url_str: str, /) -> None:
        pass

    def __truediv__(self, other: AbsUrlParseResult):
        if not isinstance(other, AbsUrlParseResult):
            name_type = type(other).__name__
            msg = f"unsupported operand type(s) for /: 'UrlParser' and '{name_type}'"
            raise TypeError(msg)
        other_path = "/" + other.path if not other.path.startswith("/") else other.path
        url = urlunparse([
            self.scheme,
            self.netloc,
            self.path + other_path,
            self.params,
            self.query,
            self.fragment
        ])
        return UrlParser(url)

    def geturl(self) -> str:
        return super().geturl().removesuffix("/")

    def format(self, *args: str, **kwargs: str):
        """Darle formato a la URL."""
        url_str = self.geturl().format(*args, **kwargs)
        return UrlParser(url_str)


class SupportsWrite(Protocol, Generic[T]):
    """Tipo Protocolo para las clases con implementación de un metodo de escritura."""
    def write(self, s: T, *args, **kwargs) -> int:
        """Metodo protocolo SupportsWrite"""


def deep_del_key(obj: Any, key_to_del: str, *, del_attrs=False) -> None:
    """Elimina la llave `key_to_del` en todos los niveles del diccionario o objecto."""
    if isinstance(obj, dict):  # Si no es un diccionario, no hacers nada.
        # recorremos todas las claves del diccionario.
        keys_to_delete = [key for key in obj if key == key_to_del]
        # Eliminar las claves encontradas.
        for key in keys_to_delete:
            del obj[key]
        # Recursivamente recorrer los subdiccionarios y aplicar la eliminación.
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                deep_del_key(value, key_to_del)
    elif isinstance(obj, list):
        for item in obj:
            deep_del_key(item, key_to_del)
    elif del_attrs and hasattr(obj, "__dir__"):
        data_dir: dict = getattr(obj, "__dir__", None)
        deep_del_key(data_dir, key_to_del)


def function_for_test(__func):
    """Decorador para funciones que solo se ejecutan en entorno de desarrollo."""
    @wraps(__func)
    def wrapper(*args, **kwargs):
        if ENVIRONMENT != "dev":
            msg = f"La función solo se puede ejecutar en entorno de desarrollo: '{__func.__name__}'"
            raise EnvironmentError(msg)
        return __func(*args, **kwargs)
    return wrapper

@function_for_test
def wait_changes_file(file: Path, /, timeout: float | None = 30) -> None:
    """
    Crea un observador que detine el tiempo de ejcución del programa, y se queda a la espera
    de que se realicen cambios en el archivo de alguna fuente externa.
    Lanza una exception de timeout si no se realizan los cambios esperados.
    
    **Nota:** Función solo para pruebas
    
    :param file: Ruta del archivo que será observado a la espera de alguna modificación.
    :type file: Path
    :param timeout: Tiempo de espera de los cambios en segundos, defecto 30 segundos.
    :type timeout: float or None
    :raises TimeOutError: Solo si se ha establecido un valor :param:`timeout`.
    :raises FileNotFoundError: Si la ruta otorgada no es de un archivo.
    """

    if FileSystemEventHandler is None:
        raise ImportError("Se requiere la libreria de desarrollo: 'wachdog'")

    if not file.is_file():
        raise FileNotFoundError(f"Archivo no encontrado: '{file}'")

    class FileChangeHandler(FileSystemEventHandler):
        """Eventos disparadores de observador del archivo."""
        def __init__(self) -> None:
            self.changed = False

        def on_modified(self, event: FileModifiedEvent) -> None:
            """Disparador cuando se modifica el archivo."""
            if Path(event.src_path) == file:
                self.changed = True

    event_handler = FileChangeHandler()
    observer = WatchDogObserver()
    observer.schedule(event_handler, file.parent)
    observer.start()
    start_time = time.time()

    while not event_handler.changed:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"No se han realizado cambios en el archivo: {file}")
        time.sleep(1)

    observer.stop()
    observer.join()
