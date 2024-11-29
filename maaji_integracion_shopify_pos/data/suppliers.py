"""
Modulo para obtener y manipular los proveedores de las tiendas.

Ver https://stocky.shopifyapps.com/api/docs/v2/suppliers/index.html
"""

from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field
from .dataclass import DataClass, DataClassFileJson, MetaDataClassFile

@dataclass
class DataSupplier(DataClass):
    """
    Estructura JSON de los proveedores de las tiendas en Shopify.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    company_name: Optional[str] = None
    account_number: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    province_code: Optional[str] = None
    country_name: Optional[str] = None
    zip: Optional[str] = None
    phone: Optional[str] = None
    phone_toll_free: Optional[str] = None
    fax: Optional[str] = None
    is_hidden: Optional[bool] = None

@dataclass
class DataSuppliersFile(DataClassFileJson):
    """Estructura JSON de los proveedores por cada tienda MAAJI."""
    # Metadatos visibles en los archivos JSON
    __metadata__: MetaDataClassFile = field(default_factory=lambda: MetaDataClassFile(True))

    maaji_co_test: list[DataSupplier] = field(default_factory=list)
    maaji_pos: list[DataSupplier] = field(default_factory=list)
    maaji_pos_outlet: list[DataSupplier] = field(default_factory=list)
