"""
Modulo para obtener y manipular las localizaciones de las tiendas.

Ver https://admin.shopify.com/store/{nombre_tienda}/settings/locations.json
"""

from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field
from .dataclass import DataClass, DataClassFileJson, MetaDataClassFile

@dataclass
class DataLocation(DataClass):
    """
    Estructura JSON de las localizaciones de las tiendas en Shopify.

    El campo `stocky_id` corresponde al id en que aparece la localización en Stocky, 
    esto es debido a que Stocky tiene una base de datos independiente a Shopify.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    province_code: Optional[str] = None
    legacy: Optional[bool] = None
    active: Optional[bool] = None
    admin_graphql_api_id: Optional[str] = None
    localized_country_name: Optional[str] = None
    localized_province_name: Optional[str] = None

    # Campos extras
    stocky_id: Optional[int] = None

@dataclass
class DataLocationsFile(DataClassFileJson):
    """Estructura JSON de las localizaciones por cada tienda MAAJI."""
    # Metadatos visibles en los archivos JSON
    __metadata__: MetaDataClassFile = field(default_factory=lambda: MetaDataClassFile(True))

    maaji_co_test: list[DataLocation] = field(default_factory=list)
    maaji_pos: list[DataLocation] = field(default_factory=list)
    maaji_pos_outlet: list[DataLocation] = field(default_factory=list)
