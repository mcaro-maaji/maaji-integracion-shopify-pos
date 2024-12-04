"""TODO: DOCS"""

from typing import Literal, NamedTuple, Optional, Any, overload
from datetime import datetime, timedelta
from urllib.parse import urlunparse, urlencode
from requests import api, RequestException
from ..config import Configuration, KeySitesShopifyStores, key_sites_shopify_stores
from ..data import (DataStocky, DataStockyFile,
                    DataSuppliersFile, DataTaxTypesFile)

KeySitesStockyAPISingle = Literal[
    "purchase_order",
    "stock_adjustment_item",
    "stock_adjustment",
    "stock_transfer",
    "supplier",
    "tax_type"
]

KeySitesStockyAPIList = Literal[
    "purchase_orders",
    "stock_adjustment_items",
    "stock_adjustments",
    "stock_transfers",
    "suppliers",
    "tax_types"
]

key_sites_stocky_api_list = (
    "purchase_orders",
    "stock_adjustment_items",
    "stock_adjustments",
    "stock_transfers",
    "suppliers",
    "tax_types"
)

KeySitesStockyAPI = KeySitesStockyAPISingle | KeySitesStockyAPIList

class StockyAPIUrlQuery(NamedTuple):
    """
    Parametros de la API de Stocky, solo funciona para limitar la cantidad de datos.
    Todos los valores se añadirán como queries en la URL.

    Ver https://stocky.shopifyapps.com/api/docs/v2/purchase_orders/index.html#Params
    """
    confirmed_since: Optional[str] = None
    updated_since: Optional[str] = None
    status: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    since_id: Optional[int] = None

def request_service(service: KeySitesStockyAPI,
                    store_key: KeySitesShopifyStores,
                    data: DataStockyFile,
                    /,
                    query=StockyAPIUrlQuery(),
                    **kwargs: Any) -> dict[str, Any]:
    """Lanzar el servicio de la API de Stocky."""
    data_stocky: DataStocky = getattr(data, store_key)
    if not data_stocky.api_key:
        raise RequestException("No se ha configurado una API key para el servicio de Stocky.")

    url_store = Configuration.get_site("shopify_store:" + store_key)
    url_service = Configuration.get_site("stocky_api", "select_" + service, **kwargs)
    url_service_query = urlencode(query._asdict())
    url = urlunparse((
        url_service.scheme,
        url_service.netloc,
        url_service.path,
        "",       # params
        url_service_query,
        url_service.fragment
    ))

    headers = {
        "Store-Name": url_store.netloc,
        "Authorization": f"API KEY={data_stocky.api_key}"
    }
    timeout = Configuration.api_service.stocky_timeout

    response = api.get(url, headers=headers, timeout=timeout)
    if response.status_code != 200:
        raise RequestException("No se pudo obtener la data en la API de Stocky.")
    return response.json()


@overload
def get_service(service: KeySitesStockyAPISingle,
                store_key: KeySitesShopifyStores,
                data: DataStockyFile,
                /,
                query=StockyAPIUrlQuery(),
                **kwargs: Any) -> dict[str, Any]: pass
@overload
def get_service(service: KeySitesStockyAPIList,
                store_key: KeySitesShopifyStores,
                data: DataStockyFile,
                /,
                query=StockyAPIUrlQuery(),
                **kwargs: Any) -> list[dict[str, Any]]: pass
def get_service(service: KeySitesStockyAPI,
                store_key: KeySitesShopifyStores,
                data: DataStockyFile,
                /,
                query=StockyAPIUrlQuery(),
                **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
    """Lanza el servicio de API de Stocky y devuelve como resultado la data del servicio."""
    data_response = request_service(service, store_key, data, query=query, **kwargs)
    if service in key_sites_stocky_api_list:
        data_response = data_response[service]
    return data_response

DataApiStockyFile = DataSuppliersFile | DataTaxTypesFile

class ApiStockyFile:
    """
    Manejador API de stocky para todo los recursos en forma de servicio junto al archivo JSON de
    cada uno:

    - Suppliers -> Proveedores
    - TaxTypes -> Tasas de impuestos
    """
    def __init__(self, data: DataStockyFile, service: DataApiStockyFile, /) -> None:
        self.data = data
        self.service = service

    def update(self, query=StockyAPIUrlQuery(), **kwargs: Any) -> None:
        """Actualiza la data del servicio desde la API de Stocky junsto al archivo JSON."""
        if isinstance(self.service, DataSuppliersFile):
            service_key = "suppliers"
        elif isinstance(self.service, DataTaxTypesFile):
            service_key = "taxtypes"
        else:
            raise TypeError("El parametro service no corresponde a algún servicio de API Stocky.")

        service_data = {}
        for store_key in key_sites_shopify_stores:
            response = get_service(service_key, store_key, self.data, query=query, **kwargs)
            service_data[store_key] = response

        service_instance = self.service.from_dict(service_data)
        self.service.replace(service_instance)
        self.service.save_file()

    def update_from_last_updated_at(self, range_time=timedelta(days=1)) -> None:
        """
        Actualiza las localizaciones solo si desde la ultima actualización no ha pasado el rango de
        tiempo dado en el parametro *range_time*.

        Por defecto, desde el ultimo día de actualización.
        """
        updated_at = self.service.__metadata__.updated_at
        if updated_at is None:
            self.update()
        else:
            diference_updated = datetime.now() - updated_at
            if diference_updated > range_time:
                self.update()
