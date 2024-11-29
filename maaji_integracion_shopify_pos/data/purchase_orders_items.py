"""
Modulo para gestionar por articulos las ordenes de compra con estructuras.
"""

from typing import Optional, Sequence, Collection, Literal
from dataclasses import dataclass, field
from .dataclass import (DataClass, DataClassFileCsv, EnumDataClassFileCsvRows as Rows,
                        FileCSVContext, _PredicatePartialRows)

@dataclass
class DataPurchaseOrderItem(DataClass):
    """
    Estructura base para la gestón de cada articulo en la orden de compra.

    Ver https://stocky.shopifyapps.com/api/docs/v2/purchase_orders/index.html
    """
    id: Optional[int] = None
    sku: Optional[str] = None
    inventory_item_id: Optional[int] = None
    product_title: Optional[str] = None
    variant_title: Optional[str] = None
    asin: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[str] = None
    retail_price: Optional[str] = None
    cost_price: Optional[str] = None
    supplier_cost_price: Optional[str] = None
    account_code: Optional[str] = None
    tax_type_id: Optional[int] = None
    accounting_tax_type: Optional[str] = None
    received_at: Optional[str] = None
    updated_at: Optional[str] = None

    # Campos extras
    bar_code: Optional[str] = None
    variant_shopify_id: Optional[str] = None

_fieldnames = DataPurchaseOrderItem.schema().fields.keys()

@dataclass
class FilePurchaseOrderItemContext(FileCSVContext):
    """Contexto para los archivos de las ordenes de compra, solo los articulos."""
    @dataclass
    class OnLoad(FileCSVContext.OnLoad[str]):
        """Parametros del evento de cargar el archivo."""
        fieldnames: Sequence[str | None] = field(default_factory=lambda: _fieldnames)
        hasfields: bool = True
        rows: Rows = Rows.ALL
        partial_rows: _PredicatePartialRows = field(default_factory=lambda: {})
        delimiter: str = ","
        lineterminator: str = "\n"

    @dataclass
    class OnSave(FileCSVContext.OnSave):
        """Parametros del evento de guardar el archivo."""
        fieldnames: Collection[str | None] = field(default_factory=lambda: _fieldnames)
        rows: Rows = Rows.ALL
        hasfields: bool = True
        partial_rows: _PredicatePartialRows = field(default_factory=lambda: {})
        extrasaction: Literal['raise', 'ignore'] = "ignore"
        delimiter: str = ","
        lineterminator: str = "\n"

    onload: OnLoad = field(default_factory=OnLoad)
    onsave: OnSave = field(default_factory=OnSave)

@dataclass
class DataPurchaseOrderItemsFile(DataClassFileCsv, DataPurchaseOrderItem):
    """Estructura para la manipulación de productos de ordenes de compra en formato CSV."""

    def getcontext(self) -> FilePurchaseOrderItemContext:
        return super().getcontext()
