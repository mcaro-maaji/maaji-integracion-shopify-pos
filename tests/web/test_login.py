from typing import overload
from pathlib import Path
from src.web.login import login_web
from .test_service import get_driver, clear_driver, BrowserDriver
from ..test_utils import load_dotenv

load_dotenv()

@overload
def test_login_web() -> None: pass
@overload
def test_login_web(clear=False) -> tuple[BrowserDriver, Path]: pass
def test_login_web(clear=True):
  [driver, dir_data] = get_driver("test_login_web")
  assert login_web(driver)
  if clear:
    clear_driver(driver, dir_data)
    return None
  else:
    return (driver, dir_data)

