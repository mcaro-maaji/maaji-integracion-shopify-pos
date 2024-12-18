"""
Modulo que mapea toda la configuración mediante un archivo JSON con valores por defecto.
"""

from typing import Literal, overload
from dataclasses import dataclass, field
from .data.dataclass import DataClass, DataClassFileJson, FileJSONContext, MetaDataClassFile
from .utils import UrlParser, WORKING_DIR

KeyWebdriverName = Literal["chrome", "edge", "firefox"]

KeySites = Literal[
    "shopify_store",
    "dynamics",
    "shopify_login",
    "shopify_admin",
    "stocky",
    "stocky_api",
    "dynamics_login"
]

SplitedStyleKeySites = Literal[
    "shopify_store:maaji_co_test",
    "shopify_store:maaji_pos",
    "shopify_store:maaji_pos_outlet",
    "dynamics:prod",
    "dynamics:uat",
    "shopify_login",
    "shopify_admin",
    "stocky",
    "stocky_api",
    "dynamics_login"
]

splited_style_key_sites = (
    "shopify_store:maaji_co_test",
    "shopify_store:maaji_pos",
    "shopify_store:maaji_pos_outlet",
    "dynamics:prod",
    "dynamics:uat",
    "shopify_login",
    "shopify_admin",
    "stocky",
    "stocky_api",
    "dynamics_login"
)

KeySitesShopifyStores = Literal[
    "maaji_co_test",
    "maaji_pos",
    "maaji_pos_outlet"
]

key_sites_shopify_stores = (
    "maaji_co_test",
    "maaji_pos",
    "maaji_pos_outlet"
)

KeySitesDynamics = Literal["prod", "uat"]

@dataclass
class ConfigWebDriver(DataClass):
    """
    Mapeo de las opciones a nivel general del webdriver en su ejecición.

    Campos
    ______
    wait_timeout: Configura el tiempo de espera de todos los momentos en los que 
                el navegador tenga que frenar la ejecución de una acción a la espera 
                de un evento, por ejemplo, esperar a que aparezca un elemento en el DOM, 
                útil si se presencia lentitud en la ejecución debido al internet.

    profile: Establece un perfil del navegador y los datos se almacenan en local, 
            esto añade al webdriver el argumento `--user-data-dir`.

     options: Ver :ref:`ConfigWebDriver.Options`.

     name_webdriver: Nombre del navegador a utilizar, por defecto "edge".
    """

    @dataclass
    class Options(DataClass):
        """
        Mapeo de las opciones del navegador.

        Campos
        ______
        add_arguments: Añadir los argumentos que se transpasan al navegador antes
                        de su ejecución:
                        `--window-size` es usado para establecer el tamaño de la ventana.
                        `--headless` ejecutar el navegador pero sin abrir una ventana del navegador.
        """
        add_arguments: list[str] = field(default_factory=lambda: ["--headless", "--log-level-3"])

    wait_timeout: float = 30
    profile: str = "profile_default"
    options: Options = field(default_factory=Options)
    name_webdriver: str = "chrome"

@dataclass
class Sites(DataClass):
    """Mapeo de todos los sitios y URL por los cuales la integración se va estar ubicando."""

    @dataclass
    class ShopifyStore(DataClass):
        """Estructura del nombre de todas las tiendas MAAJI."""
        maaji_co_test: str = "https://maaji-co-test.myshopify.com"
        maaji_pos: str = "https://maaji-pos.myshopify.com"
        maaji_pos_outlet: str = "https://maaji-pos-outlet.myshopify.com"

    @dataclass
    class Dynamics(DataClass):
        """Estructura del nombre de todas las tiendas MAAJI."""
        prod: str = "https://artmodeprod.operations.dynamics.com"
        uat: str = "https://artmodeuat.sandbox.operations.dynamics.com"

    shopify_login: str = "https://accounts.shopify.com"
    shopify_admin: str = "https://admin.shopify.com"
    shopify_store: ShopifyStore = field(default_factory=ShopifyStore)
    stocky: str = "https://stocky.shopifyapps.com"
    stocky_api: str = "https://stocky.shopifyapps.com/api/v2"
    dynamics: Dynamics = field(default_factory=Dynamics)
    dynamics_login: str = "https://login.microsoftonline.com"

    def url(self, key: SplitedStyleKeySites, /) -> UrlParser:
        """Convierte el sitio al tipo de dato `UrlParser`."""

        name_sites = key.split(":")
        obj_site: object | str | None = None
        if hasattr(self, name_sites[0]):
            obj_site = getattr(self, name_sites[0])
            if name_sites[1:] and hasattr(obj_site, name_sites[1]):
                obj_site = getattr(obj_site, name_sites[1])

        if obj_site is None:
            raise ValueError(f"No se ha encontrado un sitio valido: '{key}'")
        return UrlParser(obj_site)

    def __getitem__(self, key: SplitedStyleKeySites, /) -> UrlParser:
        return self.url(key)

    def is_site(self, key: SplitedStyleKeySites, url: str, /) -> bool:
        """Compara una URL si es un sitio que se configurado."""

        current_url = UrlParser(url)
        site = self.url(key)
        return current_url.netloc == site.netloc

    def getsite(self, url: str, /) -> SplitedStyleKeySites | None:
        """Devuelve la llave si la URL existe como sitio en la configuación o sino None."""

        for key in splited_style_key_sites:
            if self.is_site(key, url):
                return key
        return None

@dataclass
class SiteActions(DataClass):
    """Enrutamiento de los sitios para ubicar la integración en acciones."""

    @dataclass
    class ShopifyLogin(DataClass):
        """Rutas para realizar el login según el tipo de situación, primera vez ó seleccionar."""
        store_login: str = "/store-login"
        select_rid: str = "/select?rid={id}"
        lookup_rid: str = "/lookup?rid={id}&verify={token_verify}"

    @dataclass
    class ShopifyStoreAdmin(DataClass):
        """Rutas para obtener las locaclizaciones por tiendas, desde el admin Shopify."""
        select_store: str = "store/{shopify_store}"
        select_locations: str = "store/{shopify_store}/settings/locations.json"
        select_location: str = "store/{shopify_store}/settings/locations/{id}.json"

    @dataclass
    class Stocky(DataClass):
        """Rutas para acceder a las caracteristicas principales de Stocky via WEB."""
        login: str = "/login"
        select_locations: str = "/locations"
        select_api: str = "/preferences/api"
        create_api_key: str = "/accounts/create_api_key"
        create_purchase_order: str = "/purchase_orders/new"
        select_purchase_order: str = "/purchase_orders/{id}"
        edit_purchase_order: str = "/purchase_orders/{id}/edit"
        purchase_orders_add_products: str = "/purchase_orders/{id}/purchase_item_imports/new"
        purchase_orders_update_shipping: str = "/purchase_orders/{id}/edit_shipping_tax"
        purchase_orders_mark_ordered: str = "/purchase_orders/{id}/confirm"
        select_products: str = "/products"

    @dataclass
    class StockyAPI(DataClass):
        """Rutas para acceder a las caracteristicas principales de Stocky via API."""
        select_purchase_orders: str = "/purchase_orders.json"
        select_purchase_order: str = "/purchase_orders/{id}.json"
        select_stock_adjustment_items: str = "/stock_adjustment_items.json"
        select_stock_adjustment_item: str = "/stock_adjustment_items/{id}.json"
        select_stock_adjustments: str = "/stock_adjustments.json"
        select_stock_adjustment: str = "/stock_adjustments/{id}.json"
        select_stock_transfers: str = "/stock_transfers.json"
        select_stock_transfer: str = "/stock_transfers/{id}.json"
        select_suppliers: str = "/suppliers.json"
        select_supplier: str = "/suppliers/{id}.json"
        select_tax_types: str = "/tax_types.json"
        select_tax_type: str = "/tax_types/{id}.json"

    @dataclass
    class DynamcsLogin(DataClass):
        """Rutas para hacer login en el servicio de Dynamics 365."""
        login: str = "/{aad_tenant}/oauth2/token"

    @dataclass
    class Dynamics(DataClass):
        """Rutas para los servicios en Dynamics 365."""
        _api_service = "/api/services/AM_IntegrationGroup/AM_IntegrationServices"
        service_prices: str = _api_service + "/getpreciosCEGID"
        service_products: str = _api_service + "/getproductoCEGID"
        service_bills: str =_api_service + "/getfacturas"
        service_bills_shopify: str =_api_service + "/getfacturashopify"

    shopify_login: ShopifyLogin = field(default_factory=ShopifyLogin)
    shopify_admin: ShopifyStoreAdmin = field(default_factory=ShopifyStoreAdmin)
    stocky: Stocky = field(default_factory=Stocky)
    stocky_api: StockyAPI = field(default_factory=StockyAPI)
    dynamics: Dynamics = field(default_factory=Dynamics)
    dynamics_login: DynamcsLogin = field(default_factory=DynamcsLogin)

    def url(self, key_site: SplitedStyleKeySites, name_action: str, /) -> UrlParser:
        """
        Convierte las acciones de los sitios al tipo de dato `UrlParser` para la manipulación 
        de las URL, por lo general las acciones se accede mediante la propiedad `UrlParser.path`.
        """
        name_sites = key_site.split(":")
        if hasattr(self, name_sites[0]):
            obj_site_action: object = getattr(self, name_sites[0])
        else:
            raise ValueError(f"No se ha encontrado un sitio valido: '{key_site}'")

        if not hasattr(obj_site_action, name_action):
            msg = f"No se ha encontrado la acción del sitio: '{key_site}' -> '{name_action}'."
            raise ValueError(msg)

        url_action: str = getattr(obj_site_action, name_action)
        return UrlParser(url_action)

    def __getitem__(self, keys: SplitedStyleKeySites, /) -> UrlParser:
        if not isinstance(keys, tuple):
            msg = "Se esperaba un indice de tipo tupla: SiteActions['key_site', 'name_action']."
            raise TypeError(msg)
        return self.url(*keys)


@dataclass
class ConfigPurchaseOrders(DataClass):
    """
    Configuración en la creación de ordenes de compra, opciones exclusivas para este proceso.

    Campos
    ______

    timeout_add_products: Tiempo de espera para el cargue masivo de los productos
                          cuando se crea una orden de compra.
    default_supplier_name_like: Nombre para buscar el proveedor por defecto cuando
                                no se establece uno en la propia orden de compra.
    """
    timeout_add_products: float = 300 # 300 segundos = 5 minutos
    default_supplier_name_like: str = "ART MODE"


@dataclass
class ConfigApiService(DataClass):
    """configuración para los servicios de API."""
    dynamics_timeout: float = 300 # 5 minutos
    stocky_timeout: float = 300

@dataclass
class ConfigurationFile(DataClassFileJson):
    """
    Estructura base de la configuración.
    """
    # Metadatos visibles en el archivo JSON
    __metadata__: MetaDataClassFile = field(default_factory=lambda: MetaDataClassFile(True))

    webdriver: ConfigWebDriver = field(default_factory=ConfigWebDriver)
    sites: Sites = field(default_factory=Sites)
    sites_actions: SiteActions = field(default_factory=SiteActions)
    purchase_orders: ConfigPurchaseOrders = field(default_factory=ConfigPurchaseOrders)
    api_service: ConfigApiService = field(default_factory=ConfigApiService)

    @overload
    def get_site(
        self,
        key: SplitedStyleKeySites,
        /,
        **kwargs
    ) -> UrlParser: pass
    @overload
    def get_site(
        self,
        key: SplitedStyleKeySites,
        name_action: str,
        /,
        **kwargs: str
    ) -> UrlParser: pass
    def get_site(
        self,
        key: SplitedStyleKeySites,
        name_action: str | None = None,
        /,
        **kwargs: str
    ) -> UrlParser:
        """
        Obtiene el sitio + la acción, el resultado lo convierte al tipo `UrlParser`.

        :param key: Llave para identificar el sitio.
        :type key: SplitedStyleKeySites
        :param name_action: Nombre de algúna acción para el sitio.
        :type name_action: Union[str, None]
        :param kwargs: Argumentos que se pasan para formatear la URL antes de convertir.
        :type kwargs: str
        :return UrlParser: Accede a todas las propiedades de la URL.
        :raises ValueError: Si las llaves para acceder a los sitios no es valida ó si la acción
            no existe.
        """
        url_site = self.sites.url(key)
        if name_action is not None:
            url_action = self.sites_actions.url(key, name_action)
        else:
            url_action = None
        url = url_site if url_action is None else url_site / url_action
        return url.format(**kwargs)

Configuration = ConfigurationFile()
Configuration.setpath(WORKING_DIR)
Configuration.setname("configuration.json")
ConfigurationContext = FileJSONContext(onsave=FileJSONContext.OnSave(indent=4))
Configuration.setcontext(ConfigurationContext)
Configuration.load_file()
Configuration.save_file()
