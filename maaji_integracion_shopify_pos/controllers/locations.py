"""TODO: DOCS"""

from functools import lru_cache
from ..data.dataclass import FileJSONContext
from ..data.locations import DataLocationsFile
from ..web.webdriver import get_webdriver
from ..web.locations import WebLocationsFile
from ..utils import WORKING_DIR

DataLocations = DataLocationsFile()
DataLocations.setname("locations.json")
DataLocations.setpath(WORKING_DIR)
DataLocationsContext = FileJSONContext(onsave=FileJSONContext.OnSave(indent=4))
DataLocations.setcontext(DataLocationsContext)
DataLocations.load_file()

@lru_cache()
def get_weblocations():
    """Devuelve el controlador web de las localizaciones en shopify."""
    web_locations = WebLocationsFile(get_webdriver(), DataLocations)
    web_locations.update_from_last_updated_at()
    return web_locations
