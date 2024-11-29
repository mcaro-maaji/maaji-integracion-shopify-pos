"""
Modulo para obtener y manipular los datos básicos de stocky de las tiendas.

Ver https://stocky.shopifyapps.com/preferences
Ver https://stocky.shopifyapps.com/api/docs
"""

from typing import Optional
from dataclasses import dataclass, field
from .dataclass import DataClass, DataClassFileJson, MetaDataClassFile

@dataclass
class DataStocky(DataClass):
    """
    Estructura JSON de los datos básicos de stocky de las tiendas en Shopify.
    """
    api_key: Optional[str] = None

@dataclass
class DataStockyFile(DataClassFileJson):
    """Estructura JSON de los datos básicos de stocky por cada tienda MAAJI."""
    # Metadatos visibles en los archivos JSON
    __metadata__: MetaDataClassFile = field(default_factory=lambda: MetaDataClassFile(True))

    maaji_co_test: DataStocky = field(default_factory=DataStocky)
    maaji_pos: DataStocky = field(default_factory=DataStocky)
    maaji_pos_outlet: DataStocky = field(default_factory=DataStocky)
