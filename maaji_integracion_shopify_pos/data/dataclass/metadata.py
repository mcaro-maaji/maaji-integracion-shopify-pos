"""
Configuración de los metadatos, utilidad para automatizar tareas.
Por lo general para un dataclass se utiliza la palabra clave "__metadata__" como atributo.

 - Permite recopilar información clave y transmitirla entre las diferentes funcionalidades.
 - Util para manejo de archivos locales.
 - Información dinamica entre lo local y online.
 - En estructura de clase junto con la dependencia dataclass-json.
"""

from enum import Enum
from pathlib import Path
from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin as DataClass, config
from marshmallow import fields

class EnumMetaDataFileStatus(Enum):
    """
    Enum de estados de las rutas por las cuales ubicará la ruta actual del archivo.

    Ver `MetaDataClassFileStatus`.
    """
    ORIGIN = "origin"
    ON_HOLD = "onhold"
    COMPLETED = "completed"
    ON_REJECT = "onreject"

@dataclass
class MetaDataClassFileStatus(DataClass):
    """
    Rutas por las cuales se estará ubicando el archivo, util para automatizar y mover archivos.

    Estados
    -------
    :origin: Es la ruta original donde se ha leeido inicialmente el archivo.
    :onhold: Es la ruta donde debe moverse el archivo, a la espera de la ejecuión de un proceso.
    :completed: Es la ruta donde debe moverse el archivo, con una ejecición exitosa de un proceso.
    :onreject: Es la ruta donde debe moverse el archivo, con una ejeción falllida de un proceso.
    """
    origin: Optional[Path] = field(default=None, metadata=config(mm_field=fields.String()))
    onhold: Optional[Path] = field(default=None, metadata=config(mm_field=fields.String()))
    completed: Optional[Path] = field(default=None, metadata=config(mm_field=fields.String()))
    onreject: Optional[Path] = field(default=None, metadata=config(mm_field=fields.String()))

@dataclass
class MetaDataClassFile(DataClass):
    """
    Meta datos para archivos, util para tareas de automatización.

    Campos
    ------
    :visible_on_file: Hacer visible o no los metadatos en el archivo, por ejemplo, en formato JSON.
    :name: Nombre del archivo.
    :path: Ver `MetaDataClassFileStatus`.
    :path_status: Ver `EnumMetaDataFileStatus`.
    :created_at: Timestamp en que se creó el dataclass.
    :updated_at: Timestamp en que se actualizó el dataclass.
    :last_accessed_at: Timestamp del ultimo acceso a el dataclass.
    """
    visible_on_file: bool = False
    name: Optional[str] = None
    path: MetaDataClassFileStatus = field(default_factory=MetaDataClassFileStatus)
    path_status: EnumMetaDataFileStatus = EnumMetaDataFileStatus.ORIGIN # Por defecto
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
