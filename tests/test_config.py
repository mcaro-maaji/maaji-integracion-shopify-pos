import json
from typing import overload
from pathlib import Path
from functools import lru_cache
from src.config import BotConfiguration as BotConfig
from src.utils import load_dotenv
from .test_utils import ROOT_DIR_TEST

TEST_PATH_FILE_CONFIG = ROOT_DIR_TEST / "config.test.json"

@overload
def load_config_and_dotenv(__id_exec: str) -> str: pass
@overload
def load_config_and_dotenv(__id_exec: int) -> int: pass
@lru_cache(None)
def load_config_and_dotenv(__id_exec: str | int):
  load_dotenv()
  BotConfig.load_from_json_file(TEST_PATH_FILE_CONFIG)
  return __id_exec

def test_load_config():
  load_config_and_dotenv(1)
  assert BotConfig.sites != []

def test_save_config():
  load_config_and_dotenv(1)
  data_test = "::TEST::"
  BotConfig.suppliers = data_test
  BotConfig.save_config(TEST_PATH_FILE_CONFIG)
  with open(TEST_PATH_FILE_CONFIG) as file:
    json_data: dict = json.load(file)
  assert json_data.get("suppliers") == data_test

def test_get_site():
  load_config_and_dotenv(1)
  site_shopify_login = BotConfig.sites.get("shopify_login")
  assert site_shopify_login

def test_get_site_actions():
  load_config_and_dotenv(1)
  site_actions_stocky_login = BotConfig.get_site_action("shopify_stocky", "login")
  assert site_actions_stocky_login

def test_is_url_current_site():
  load_config_and_dotenv(1)
  is_url_current_site = BotConfig.is_url_current_site(BotConfig.sites["shopify_login"], "shopify_login")
  not_is_url_current_site = BotConfig.is_url_current_site(BotConfig.sites["shopify_login"], "shopify_stocky_api")
  assert is_url_current_site
  assert not not_is_url_current_site

def test_get_path_webdriver_profile():
  load_config_and_dotenv(1)
  name_dir_data_webdrier = BotConfig.get_dir_webdriver_profile().name
  assert name_dir_data_webdrier.startswith("dev")

def test_request_stocky_api():
  load_config_and_dotenv(1)
  BotConfig.suppliers = []
  BotConfig.load_from_stocky_api()
  BotConfig.save_config()
  # Advertencia: Solo funciona si efectivamente hay proveedores configurados en Stocky
  assert BotConfig.suppliers != []

