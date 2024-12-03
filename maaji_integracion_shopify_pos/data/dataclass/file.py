"""
Utilidades abstractas para la manipulación de archivos con clases.
"""

from typing import final, Any
from pathlib import Path
from copy import deepcopy
from io import TextIOWrapper
from datetime import datetime
from shutil import move as move_file
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin as DataClass
from maaji_integracion_shopify_pos.utils import deep_del_key
from .metadata import MetaDataClassFile, EnumMetaDataFileStatus

@dataclass
class FileContext:
    """
    Clase abstracta para definir contexto para los eventos de funciones del dataclass
    en la gestion de archivos, por ejemplo, para cargar y guardar un archivo.

    Los atributos se definen como dataclass debido a que son parametros de las funciones
    que son despachadas como eventos y cambian el comportamiento del archivo.
    """
    @dataclass
    class OnLoad:
        """Parametros del evento de cargar el archivo."""

    @dataclass
    class OnSave:
        """Parametros del evento de guardar el archivo."""

    onload: OnLoad = field(default_factory=OnLoad)
    onsave: OnSave = field(default_factory=OnSave)


@dataclass
class DataClassFile(DataClass):
    """Estructura base para la manipulación de archivos con clases."""

    __metadata__: MetaDataClassFile = field(default_factory=MetaDataClassFile)

    @final
    def metadata_update(self) -> dict[str, Any]:
        """
        Actualiza los metadatos despues de un evento, por ejemplo, al guardar un archivo.

        Devuelve un diccionario con los metadatos anteriores a los cambios.
        """
        current_datetime = datetime.now()
        copy_old_metadata = deepcopy(self.__metadata__.__dict__)
        if not self.__metadata__.created_at:
            self.__metadata__.created_at = current_datetime
        if not self.__metadata__.updated_at:
            self.__metadata__.updated_at = current_datetime
        return copy_old_metadata

    def to_dict(self, encode_json=False) -> dict[str, Any]:
        data_dict = super().to_dict(encode_json)
        if self.__metadata__.visible_on_file:
            return data_dict

        # los metadatos del dataclass padre sobrecriben los sub-dataclass por eso se deben eliminar.
        deep_del_key(data_dict, "__metadata__", del_attrs=True)
        return data_dict

    @final
    def getpath(self) -> Path | None:
        """
        Obtener la ruta del directorio del archivo dependiendo del estado del archivo seleccionado.
        """
        key = self.__metadata__.path_status.value
        path = getattr(self.__metadata__.path, key)
        return path

    @final
    def getname(self) -> str | None:
        """Obtener el nombre del archivo."""
        return self.__metadata__.name

    @final
    def getstatus(self) -> EnumMetaDataFileStatus:
        """Obtener el estado la ruta del archivo."""
        return self.__metadata__.path_status

    @final
    def setstatus(self, status: EnumMetaDataFileStatus, /) -> None:
        """
        Cambia el estado de ruta del archivo, por lo cual, las funciones `load_file`, y `save_file`
        accederan al archivo dependiendo del estado.
        """
        self.__metadata__.path_status = status

    @final
    def setname(self, name: str, /) -> None:
        """Cambiar el nombre del archivo."""
        self.__metadata__.name = name

    @final
    def setpath(self, path: str | Path, status=EnumMetaDataFileStatus.ORIGIN, /) -> None:
        """Cambia una ruta del archivo dependiendo del estado."""
        path = Path(path)
        path = path.absolute()
        setattr(self.__metadata__.path, status.value, path)

    __context = FileContext()

    # @final
    def getcontext(self) -> FileContext:
        """Devuelve el contexto que se ha configurado al archivo."""
        return self.__context

    @final
    def setcontext(self, value: FileContext, /):
        """Establece el contexto para el archivo."""
        if isinstance(value, FileContext):
            self.__context = value
        else:
            raise TypeError("El valor debe ser de tipo: 'FileContext'")

    def onload_file(self, __file: TextIOWrapper, __context: FileContext, /) -> int:
        """
        Metodo de evento, util para definir comportamiento de la lectura de un archivo
        antes del cierre automatico.

        Evento: al leer el archivo.

        :param __file: StreamIO del archivo al ejecutar la función `load_file`.
        :type __file: TextIOWrapper
        :param __context: Contexto del archivo en que se invoca el evento.
        :type __context: FileContext
        :returns int: Número de estado de salida "exit status".
        """
        return 0

    @final
    def load_file(self,
                  *,
                  context: FileContext | None = None,
                  skip_err=True,
                  encoding="utf-8") -> None:
        """
        Cargar el archivo, la función `onload_file` define el comportamiento del dataclass.

        :param context: Contexto en que se manipula el archivo.
        :type context: FileContext | None
        :param skip_err: Saltar el error que se presente, por ejemplo, `FileNotFoundError`.
        :param encoding: Codificación en que se abrirá el archivo, por defect, "utf-8".
        :type encoding: str
        """
        if context is None:
            context = self.getcontext()
        path = self.getpath()
        name = self.getname()
        if not path or not name:
            return None
        try:
            with open(path / name, encoding=encoding) as file:
                status_err = self.onload_file(file, context)
                if not status_err:
                    self.metadata_update()
                    self.__metadata__.last_accessed_at = datetime.now()
        except FileNotFoundError as err:
            err.strerror = "Archivo no encontrado para el dataclass"
            if not skip_err:
                raise err
        return None

    def onsave_file(self, __file: TextIOWrapper, __context: FileContext, /) -> int:
        """
        Metodo de evento, util para definir comportamiento de la escritura de un archivo
        antes del cierre automatico.

        Evento: al guardar el archivo.

        :param __file: StreamIO del archivo al ejecutar la función `save_file`.
        :type __file: TextIOWrapper
        :param __context: Contexto del archivo en que se invoca el evento.
        :type __context: FileContext
        :returns int: Número de estado de salida "exit status".
        """
        return 0

    @final
    def save_file(self,
                  *,
                  context: FileContext | None = None,
                  skip_err=True,
                  encoding="utf-8") -> None:
        """
        Guarda el archivo escribiendo el texto devuelto por la función `onload_file`.

        :param context: Contexto en que se manipula el archivo.
        :type context: FileContext | None
        :param skip_err: Saltar el error que se presente, por ejemplo, `FileNotFoundError`.
        :param encoding: Codificación en que se guardará el archivo, por defecto "utf-8".
        :type encoding: str
        """
        if context is None:
            context = self.getcontext()
        path = self.getpath()
        name = self.getname()
        if not path or not name:
            return None
        path.mkdir(mode=511, parents=True, exist_ok=True)
        copy_old_metadata = self.metadata_update()
        try:
            with open(path / name, "w", encoding=encoding) as file:
                self.__metadata__.updated_at = datetime.now()
                status_err = self.onsave_file(file, context)
                if status_err:
                    self.__metadata__.__dict__.update(copy_old_metadata)
        except FileNotFoundError as err:
            err.strerror = "Archivo no encontrado para el dataclass"
            if not skip_err:
                raise err
        return None

    @final
    def replace(self, __dataclass: DataClass, replace_metadata=False, /) -> None:
        """Reemplaza los campos de un dataclass con otro."""
        if not isinstance(__dataclass, DataClass):
            raise TypeError("Se esperaba un tipo 'DataClass' como valor.")

        fieldnames = self.schema().fields.keys()
        dtcls_fieldnames = list(__dataclass.schema().fields.keys())
        if not replace_metadata and "__metadata__" in dtcls_fieldnames:
            dtcls_fieldnames.remove("__metadata__")
        new_dict = {key: __dataclass.__dict__[key] for key in fieldnames if key in dtcls_fieldnames}
        self.__dict__.update(new_dict)

    @final
    def move_file(self, status: EnumMetaDataFileStatus) -> None:
        """Mueve el archivo dependiendo del estado del mismo."""
        name = self.getname()
        if self.getstatus() == status:
            return None
        current_path = self.getpath()
        self.setstatus(status)
        new_path = self.getpath()

        if current_path is None or new_path is None:
            raise TypeError("No se puede mover el archivo: La ruta fuente o destino es nulo.")

        current_path.mkdir(mode=511, parents=True, exist_ok=True)
        new_path.mkdir(mode=511, parents=True, exist_ok=True)
        move_file(current_path / name, new_path / name)
        return None
