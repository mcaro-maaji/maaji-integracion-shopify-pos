"""
Modulo para obtener y manipular los impuestos de las tiendas.

Ver https://stocky.shopifyapps.com/api/docs/v2/tax_types/index.html
"""

from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field
from .dataclass import DataClass, DataClassFileJson, MetaDataClassFile

@dataclass
class DataTaxType(DataClass):
    """
    Estructura JSON de los impuestos de las tiendas en Shopify.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
    tax_rate: Optional[str] = None
    purpose: Optional[str] = None
    accounting_tax_type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class DataTaxTypesFile(DataClassFileJson):
    """Estructura JSON de los impuestos por cada tienda MAAJI."""
    # Metadatos visibles en los archivos JSON
    __metadata__: MetaDataClassFile = field(default_factory=lambda: MetaDataClassFile(True))

    maaji_co_test: list[DataTaxType] = field(default_factory=list)
    maaji_pos: list[DataTaxType] = field(default_factory=list)
    maaji_pos_outlet: list[DataTaxType] = field(default_factory=list)
