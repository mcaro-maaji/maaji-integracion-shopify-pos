"""
Modulo para gestionar de las ordenes de compra con estructuras.
"""

from typing import Optional, Sequence, Collection, Literal, Self
from copy import deepcopy
from io import TextIOWrapper
from types import SimpleNamespace
from datetime import datetime, date
from dataclasses import dataclass, field
from functools import partial as func_partial
from marshmallow import fields
from .dataclass import (DataClass, config, DataClassFileCsv, EnumDataClassFileCsvRows as Rows,
                        FileCSVContext, _PredicatePartialRows)
from .purchase_orders_items import (DataPurchaseOrderItem, DataPurchaseOrderItemsFile,
                                    FilePurchaseOrderItemContext)
from ..utils import SupportsWrite

@dataclass
class DataPurchaseOrder(DataClass):
    """
    Estructura base para las ordenes de compra.

    Ver https://stocky.shopifyapps.com/api/docs/v2/purchase_orders/index.html
    """

    id: Optional[str] = None
    number: Optional[str] = None
    sequential_id: Optional[int] = None
    invoice_number: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    generated_at: Optional[datetime] = None
    ordered_at: Optional[datetime] = None
    expected_on: Optional[date] = field(default=None, metadata=config(mm_field=fields.Date()))
    ship_on: Optional[date] = field(default=None, metadata=config(mm_field=fields.Date()))
    payment_due_on: Optional[date] = field(default=None, metadata=config(mm_field=fields.Date()))
    archived: Optional[bool] = None
    supplier_name: Optional[str] = None
    supplier_id: Optional[int] = None
    currency: Optional[str] = None
    shopify_receive_location_id: Optional[int] = None
    paid: Optional[bool] = None
    adjustments: Optional[float] = None
    adjustments_local: Optional[float] = None
    shipping: Optional[float] = None
    shipping_local: Optional[float] = None
    shipping_tax_type: Optional[int] = None
    invoice_date: Optional[date] = field(default=None, metadata=config(mm_field=fields.Date()))
    purchase_items: Optional[list[DataPurchaseOrderItem]] = field(default_factory=lambda: [])

    # Campos extras
    shopify_store_key_name: Optional[str] = None # ej. maaji_co_pos
    supplier_order: Optional[str] = None
    shopify_address_shipping_id: Optional[int] = None
    payment_on: Optional[datetime] = None
    cancel_on: Optional[str] = None
    amount_items: Optional[float] = None
    amount_paid: Optional[float] = None
    purchase_order_notes: Optional[str] = None
    supplier_notes: Optional[str] = None

_fieldnames = list(DataPurchaseOrder.schema().fields.keys())
_fieldnames.remove("purchase_items")

@dataclass
class FilePurchaseOrderContext(FileCSVContext):
    """Contexto para los archivos de las ordenes de compra."""
    @dataclass
    class OnLoad(FileCSVContext.OnLoad[str]):
        """Parametros del evento de cargar el archivo."""
        fieldnames: Sequence[str | None] = field(default_factory=lambda: _fieldnames)
        hasfields: bool = True
        rows: Rows = Rows.FIRST
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
    purchase_items_context: FilePurchaseOrderItemContext = field(default_factory=FilePurchaseOrderItemContext)
    purchase_items_fstr: str = "purchase_items[{}]"

@dataclass
class DataPurchaseOrdersFile(DataClassFileCsv, DataPurchaseOrder):
    """Estructura para la manipulación de ordenes de compra en formato CSV."""
    purchase_items: list[DataPurchaseOrderItemsFile] = field(default_factory=lambda: [])

    def getcontext(self) -> FilePurchaseOrderContext:
        return super().getcontext()

    @classmethod
    def getfieldnames(cls, context: FilePurchaseOrderContext, /) -> list[str]:
        """
        Devuelve los nombre de los campos, dando prioridad a los de articulos y formateado.

        Valida si el tamaño de los campos coinciden entre el contexto de la orden de compra y
        el contexto de `purchase_items`, los campos se homologan mediante esta función, los campos
        que esten en el contexto con el valor `None` será reemplazado por el del otro contexto
        en orden.
        """
        len_onload_fields_items = len(context.purchase_items_context.onload.fieldnames)
        len_onload_fields = len(context.onload.fieldnames)
        if len_onload_fields != len_onload_fields_items:
            msg = "Los campos de la orden de compra no coinciden en tamaño en el contexto."
            raise ValueError(msg)

        fieldnames_items = context.purchase_items_context.onsave.fieldnames
        fstr = context.purchase_items_fstr
        fieldnames_items = [None if fn is None else fstr.format(fn) for fn in fieldnames_items]
        fieldnames = []
        # prioriza los campos de los articulos: purchase_items
        for idx, value in enumerate(context.onsave.fieldnames):
            if value is None:
                value = fieldnames_items[idx]
            fieldnames.append(value)
        return fieldnames

    @classmethod
    def from_csv(cls, f: TextIOWrapper, context: FilePurchaseOrderContext, /) -> Self:
        """Cargar en formato CSV, crea la instancia y la devuelve."""
        items = DataPurchaseOrderItemsFile.from_csv(f, context.purchase_items_context)
        f.seek(0)
        instance = super().from_csv(f, context)
        for row in instance.__csv_rows__:
            row.purchase_items = items.__csv_rows__
        return instance

    def to_csv(self,
               f: SupportsWrite[str],
               context: FilePurchaseOrderContext,
               /) -> SupportsWrite[str]:
        """Guarda la orden de compra en formato CSV."""
        fstr = context.purchase_items_fstr
        __csv_rows__ = deepcopy(self.__csv_rows__)
        len_rows_purchase = len(self.__csv_rows__) - 1
        for idx, purchase_item in enumerate(self.purchase_items):
            if idx <= len_rows_purchase:
                row_purchase = self.__csv_rows__[idx]
                is_new_purchase = False
            else:
                row_purchase = self.__class__()
                is_new_purchase = True

            row_purchase.purchase_items = purchase_item
            dict_row_purchase = row_purchase.to_dict()
            dict_items: dict = dict_row_purchase.pop("purchase_items")
            dict_items = {fstr.format(key): value for key, value in dict_items.items()}
            dict_row_purchase.update(dict_items)
            # Simular un dataclass
            row_purchase = SimpleNamespace()
            # Obligatorio añadir el metodo to_dict
            row_purchase.to_dict = func_partial(lambda x: x, dict_row_purchase)

            if is_new_purchase:
                self.__csv_rows__.append(row_purchase)
            else:
                self.__csv_rows__[idx] = row_purchase

        old_fieldnames = context.onsave.fieldnames
        fieldnames = DataPurchaseOrdersFile.getfieldnames(context)
        context.onsave.fieldnames = fieldnames
        super().to_csv(f, context)
        self.__csv_rows__ = __csv_rows__
        context.onsave.fieldnames = old_fieldnames
        return f
    