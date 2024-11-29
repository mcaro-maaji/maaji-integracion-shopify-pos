"""
Modulo para manipular archivos por medio de clases en Python.
"""

__all__ = [
    "DataClass", "DataClassGlobalConfig", "config",
    "MetaDataClassFile", "MetaDataClassFileStatus", "EnumMetaDataFileStatus",
    "DataClassFile",
    "DataClassFileJson", "FileJSONContext",
    "DataClassFileCsv", "EnumDataClassFileCsvRows", "_PredicatePartialRows", "FileCSVContext"
]

from typing import TypeVar
from datetime import datetime, date
from dataclasses_json import (DataClassJsonMixin as DataClass,
                              global_config as DataClassGlobalConfig, config)
from .metadata import MetaDataClassFile, MetaDataClassFileStatus, EnumMetaDataFileStatus
from .file import DataClassFile
from .file_json import DataClassFileJson, FileJSONContext
from .file_csv import (DataClassFileCsv, EnumDataClassFileCsvRows,
                       _PredicatePartialRows, FileCSVContext)

T = TypeVar("T")

def optional_decoder(type_data: type[T]) -> type[T] | None:
    """Crea un decodificador opcional, convierte los valores vacios en opcionales "None"."""
    def decoder(*args, **kwargs) -> T:
        if not all(args):
            return None
        return type_data(*args, **kwargs)
    return decoder

DataClassGlobalConfig.encoders[datetime] = datetime.isoformat
DataClassGlobalConfig.decoders[datetime] = optional_decoder(datetime.fromisoformat)
DataClassGlobalConfig.encoders[date] = date.isoformat
DataClassGlobalConfig.decoders[date] = optional_decoder(date.fromisoformat)
DataClassGlobalConfig.decoders[float] = optional_decoder(float)
DataClassGlobalConfig.decoders[int] = optional_decoder(int)
