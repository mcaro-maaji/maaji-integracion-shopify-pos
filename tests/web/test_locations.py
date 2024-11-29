from src.web.locations import get_locations
from .test_service import clear_driver
from .test_login import test_login_web

def test_get_locations():
  [driver, dir_data] = test_login_web(False)
  locations = get_locations(driver)
  assert locations is not None

  clear_driver(driver, dir_data)
