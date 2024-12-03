"""TODO: DOCS"""

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

WebLocations = WebLocationsFile(get_webdriver(), DataLocations)
WebLocations.update_from_last_updated_at()
