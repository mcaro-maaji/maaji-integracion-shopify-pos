"""TODO: DOCS"""

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

WebStocky = WebStockyFile(get_webdriver(), DataStocky)
WebStocky.update_from_last_updated_at()

DataSuppliers = DataSuppliersFile()
DataSuppliers.setname("suppliers.json")
DataSuppliers.setpath(WORKING_DIR)
DataSuppliersContext = FileJSONContext(onsave=FileJSONContext.OnSave(indent=4))
DataSuppliers.setcontext(DataSuppliersContext)
DataSuppliers.load_file()

ApiStockySuppliers = ApiStockyFile(DataStocky, DataSuppliers)
ApiStockySuppliers.update_from_last_updated_at()
