"""Modulo para manipulación de archivos JSON por medio de dataclasses."""

from typing import Any, Callable
from io import TextIOWrapper
from json import JSONDecodeError
from dataclasses import dataclass, field, asdict
from .file import DataClassFile, FileContext

@dataclass
class FileJSONContext(FileContext):
    """Contexto para los archivos en formato JSON."""
    @dataclass
    class OnLoad(FileContext.OnLoad):
        """Parametros del evento de cargar el archivo."""
        parse_float: Any | None = None
        parse_int: Any | None = None
        parse_constant: Any | None = None
        infer_missing: bool = False
        kw: dict[str, Any] = field(default_factory=lambda: {})

    @dataclass
    class OnSave(FileContext.OnSave):
        """Parametros del evento de guardar el archivo."""
        skipkeys: bool = False
        ensure_ascii: bool = True
        check_circular: bool = True
        allow_nan: bool = True
        indent: int | str | None = None
        separators: tuple[str, str] | None = None
        default: Callable[[], Any] | None = None
        sort_keys: bool = False
        kw: dict[str, Any] = field(default_factory=lambda: {})

    onload: OnLoad = field(default_factory=OnLoad)
    onsave: OnSave = field(default_factory=OnSave)

@dataclass
class DataClassFileJson(DataClassFile):
    """Estructura base para la manipulación de archivos JSON con clases."""

    def getcontext(self) -> FileJSONContext:
        return super().getcontext()

    def onload_file(self, __file: TextIOWrapper, context: FileJSONContext, /) -> int:
        """
        Metodo de evento, util para definir comportamiento de la lectura de un archivo JSON
        antes del cierre automatico.

        Evento: al leer el archivo.

        :param __file: StreamIO del archivo al ejecutar la función `load_file`.
        :type __file: TextIOWrapper
        :param context: Contexto del archivo en que se invoca el evento.
        :type context: FileJSONContext
        """
        json_text = __file.read()
        params = asdict(context.onload)
        kwargs = params.pop("kw")
        params.update(kwargs)

        try:
            json_config = self.__class__.from_json(json_text, **params)
        except JSONDecodeError as err:
            err.args = (f"Error al cargar el archivo: '{__file.name}'",)
            raise err
        self.replace(json_config)
        self.__metadata__ = json_config.__metadata__
        return 0

    def onsave_file(self, __file: TextIOWrapper, context: FileContext, /) -> int:
        """
        Metodo de evento, util para definir comportamiento de la escritura de un archivo JSON
        antes del cierre automatico.

        Evento: al guardar el archivo.

        :param __file: StreamIO del archivo al ejecutar la función `save_file`.
        :type __file: TextIOWrapper
        :param context: Contexto del archivo en que se invoca el evento.
        :type context: FileContext
        :returns str: Texto CSV el cual se escribirá en el archivo.
        """
        params = asdict(context.onsave)
        kwargs = params.pop("kw")
        params.update(kwargs)
        json_text = self.to_json(**params)
        __file.write(json_text)
        return 0
