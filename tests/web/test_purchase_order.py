from src.web.login import login_web
from src.web.locations import get_locations_stocky
from src.web.purchase_orders import try_create_purchase_order
from src.data import DataPurchaseOrder
from src.utils import WORKING_DIR
from .test_service import get_driver, rm_dir_data, BotConfig

file_purchase_order = WORKING_DIR / "data/tests/pedido_de_compra/Entrada/Compra 2021-02-14 08-00-00 FEV055555.csv"
test_data_purchase_order = DataPurchaseOrder(file_purchase_order)

def test_create_purchase_order():
  [driver, dir_data] = get_driver("test_create_purchase_order")
  login_web(driver)
  if not BotConfig.locations:
    BotConfig.locations = get_locations_stocky(driver) or []
    BotConfig.save_config()

  assert try_create_purchase_order(driver, test_data_purchase_order)
  "breakpoint"
  driver.quit()
  rm_dir_data(dir_data)

