"""TODO: DOCS"""

from functools import lru_cache
from ..data.dataclass import FileJSONContext
from ..data import DataStockyFile, DataSuppliersFile
from ..web.webdriver import get_webdriver
from ..web.stocky import WebStockyFile
from ..api.stocky import ApiStockyFile
from ..utils import WORKING_DIR

DataStocky = DataStockyFile()
DataStocky.setname("stocky.json")
DataStocky.setpath(WORKING_DIR)
DataStockyContext = FileJSONContext(onsave=FileJSONContext.OnSave(indent=4))
DataStocky.setcontext(DataStockyContext)
DataStocky.load_file()

@lru_cache()
def get_webstocky():
    """Devuelve el controlador web de los datos básicos de stocky."""
    web_stocky = WebStockyFile(get_webdriver(), DataStocky)
    web_stocky.update_from_last_updated_at()
    return web_stocky

DataSuppliers = DataSuppliersFile()
DataSuppliers.setname("suppliers.json")
DataSuppliers.setpath(WORKING_DIR)
DataSuppliersContext = FileJSONContext(onsave=FileJSONContext.OnSave(indent=4))
DataSuppliers.setcontext(DataSuppliersContext)
DataSuppliers.load_file()

@lru_cache()
def get_apistocky_suppliers():
    """Devuelve el controlador api de los proveedores en stocky."""
    api_stocky_suppliers = ApiStockyFile(DataStocky, DataSuppliers)
    api_stocky_suppliers.update_from_last_updated_at()
    return api_stocky_suppliers
