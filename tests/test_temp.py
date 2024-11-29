from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

@dataclass
class Supplier(DataClassJsonMixin):
    """
    Estructura JSON de las proveedores de las tiendas en Shopify.
    """
    id: int
    name: str
    created_at: str

    _hello = []

    def peto(self): pass

print(list(Supplier.schema().fields.keys()))

