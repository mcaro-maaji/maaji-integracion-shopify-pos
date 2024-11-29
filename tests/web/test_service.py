from pathlib import Path
from shutil import rmtree
from src.web.service import get_driver as _get_driver
from ..test_config import BotConfig, load_config_and_dotenv

def get_driver(test_web_profile: str):
  load_config_and_dotenv(test_web_profile)
  BotConfig.webdriver['profile'] = test_web_profile
  dir_data = BotConfig.get_dir_webdriver_profile(test_web_profile)
  driver = _get_driver(test_web_profile)
  return (driver, dir_data)

def rm_dir_data(dir_data: Path, ignore_errors=True):
  rmtree(dir_data, ignore_errors)

def test_get_driver_profiles():
  [driver_1, dir_data_1] = get_driver("test_profiles_1")
  [driver_2, _] = get_driver("test_profiles_1")
  [driver_3, dir_data_3] = get_driver("test_profiles_2")
  assert driver_1.session_id == driver_2.session_id
  assert driver_1.session_id != driver_3.session_id
  
  driver_1.quit()
  driver_3.quit()
  rm_dir_data(dir_data_1)
  rm_dir_data(dir_data_3)

