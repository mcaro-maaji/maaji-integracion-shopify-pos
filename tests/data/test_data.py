from src.data import DataPurchaseOrder, DataRows
from ..test_utils import WORKING_DIR

FILES_PURCHASE_ORDERS = list((WORKING_DIR / r"data\tests\pedido_de_compra\Entrada").glob("*.csv"))

JSON_PURCHASE_ORDER = """
[
  {
    "sku": "PT1715KSTPRUECO44-6K",
    "bar_code": "7702781024833",
    "variant_shopify_id": 123123123,
    "quantity": 5,
    "cost_price": 150000,
    "supplier_id": 2775094,
    "currency": "COP",
    "amount_paid": 120000.00,
    "payment_due_on": null,
    "paid": true,
    "payment_on": null,
    "adjustments": 3000.00,
    "shipping": 50000.00,
    "shipping_tax_type_id": 1001,
    "shopify_receive_location_id": 72046280749,
    "invoice_number": "FEV055555",
    "sequence_invoice_number": "055555",
    "supplier_order_number": "PV-000331",
    "order_date": "2021-02-09",
    "invoice_date": "2021-02-10",
    "expected_on": "2021-02-22",
    "ship_on": "2021-02-24",
    "cancel_date": "2021-02-24"
  }
]
"""

def test_create_obj_purchase_orders():
  assert FILES_PURCHASE_ORDERS != []
  purchase_order_csv = DataPurchaseOrder.from_csv(FILES_PURCHASE_ORDERS[0])
  assert purchase_order_csv.id == None
  assert isinstance(purchase_order_csv.sku, DataRows)
  assert purchase_order_csv.sku.first_row == "PT1715KSTPRUECO44-6K"
  assert purchase_order_csv._to_iter_dict(slice(1)), list
  assert isinstance(purchase_order_csv._to_json(slice(1)), str)

  purchase_order_json = DataPurchaseOrder.from_json(JSON_PURCHASE_ORDER)
  assert purchase_order_json.id == None
  assert isinstance(purchase_order_json.sku, DataRows)
  assert purchase_order_json.sku.first_row == "PT1715KSTPRUECO44-6K"
  assert purchase_order_json._to_iter_dict(slice(1)), list
  assert isinstance(purchase_order_json._to_json(slice(1)), str)

