"""Modulo para manipulación de archivos CSV por medio de dataclasses."""

from typing import (TypeVar, TypeAlias, Any, TypeGuard, Self, Iterable, Sequence,
                    Collection, Literal, Generic, Callable)
from enum import Enum
from io import TextIOWrapper
from dataclasses import dataclass, field
from csv import DictReader as CsvDictReader, DictWriter as CsvDictWriter, Dialect as _Dialect
from maaji_integracion_shopify_pos.utils import SupportsWrite
from .file import DataClassFile, FileContext

T = TypeVar("T")
_QuotingType: TypeAlias = int
_DialectLike: TypeAlias = str | _Dialect | type[_Dialect]
_PredicatePartialRows = dict[str, str | Any | Callable[[str | Any], bool]]

class EnumDataClassFileCsvRows(Enum):
    """
    Establece el comportamiento de lectura y de escritura de las filas en los archivos CSV.

    :ALL: todas las filas.
    :FIRST: solo la primera fila.
    :PARTIAL: parcialmente las filas según criterios de busqueda coincidentes.
    """
    ALL = "all"
    FIRST = "first"
    PARTIAL = "partial"

@dataclass
class FileCSVContext(FileContext):
    """Contexto para la manipulación de archivos en formato CSV."""
    @dataclass
    class OnLoad(FileContext.OnLoad, Generic[T]):
        """Parametros del evento de cargar el archivo."""
        fieldnames: Sequence[T]
        rows: EnumDataClassFileCsvRows = EnumDataClassFileCsvRows.ALL
        partial_rows: _PredicatePartialRows = field(default_factory=lambda: {})
        hasfields: bool = True
        restkey: T | None = None
        restval: str | Any | None = None
        dialect: _DialectLike = "excel"
        delimiter: str = ","
        quotechar: str | None = '"'
        escapechar: str | None = None
        doublequote: bool = True
        skipinitialspace: bool = False
        lineterminator: str = "\r\n"
        quoting: _QuotingType = 0
        strict: bool = False

    @dataclass
    class OnSave(FileContext.OnSave):
        """Parametros del evento de guardar el archivo."""
        fieldnames: Collection[str]
        rows: EnumDataClassFileCsvRows = EnumDataClassFileCsvRows.ALL
        hasfields: bool = True
        partial_rows: _PredicatePartialRows = field(default_factory=lambda: {})
        restval: Any | None = ""
        extrasaction: Literal['raise', 'ignore'] = "raise"
        dialect: _DialectLike = "excel"
        delimiter: str = ","
        quotechar: str | None = '"'
        escapechar: str | None = None
        doublequote: bool = True
        skipinitialspace: bool = False
        lineterminator: str = "\r\n"
        quoting: _QuotingType = 0
        strict: bool = False

    onload: OnLoad
    onsave: OnSave

@dataclass
class DataClassFileCsv(DataClassFile):
    """Estructura base para la manipulación de archivos CSV con clases."""

    def __post_init__(self):
        self.__csv_row_select = 0
        self.__csv_rows = []

    def getcontext(self) -> FileCSVContext:
        return super().getcontext()

    @classmethod
    def is_csv_rows(cls, value: Any) -> TypeGuard[list[Self]]:
        """Comprueba si el parametro `value` es valido para al atributo `csv_rows`."""
        if not isinstance(value, list):
            return False
        return len(value) == 0 or all((isinstance(item, cls) for item in value))

    @property
    def __csv_rows__(self) -> list[Self]:
        """Devuelve las filas del CSV."""
        return self.__csv_rows

    @__csv_rows__.setter
    def __csv_rows__(self, value: Any) -> None:
        if not self.__class__.is_csv_rows(value):
            raise TypeError("No se puede asignar el valor, como filas del CSV.")
        self.__csv_rows = value

    def setrow(self, num: int = 1, /) -> None:
        """
        Establece todas los campos del dataclass con los de la fila seleccionada del CSV.
        
        :param num: El número de la fila seleccionada, por defecto es 1, primera fila,
                    valores negativos asigna desde la ultima fila.
        :type num: int = 1
        """
        length = len(self.__csv_rows__)
        if num == 0 or length == 0:
            return None
        if abs(num) <= length:
            idx_row = num - 1 if num > 0 else num
            csv_row = self.__csv_rows__[idx_row]
            setattr(csv_row, "__metadata__", self.__metadata__)
            self.replace(csv_row)
        else:
            msg = f"El numero de fila '{num}' está fuera del rango del archivo CSV."
            raise IndexError(msg)
        self.__csv_row_select = num
        return None

    def flush_row(self) -> None:
        """Establece los cambios del dataclass en la fila del CSV seleccionada."""
        num = self.__csv_row_select
        if num != 0:
            idx_row = num - 1 if num > 0 else num
            self.__csv_rows__[idx_row].replace(self)

    @classmethod
    def from_csv(cls, f: Iterable[str], context: FileCSVContext, /) -> Self:
        """
        Convertir el formato CSV a un listado de diccionarios.
        """
        params = context.onload
        data_rows = []
        try:
            if params.hasfields:
                next(f) # ignorar los campos/encabezados del CSV.
            csv_reader = CsvDictReader(f,
                                       params.fieldnames,
                                       params.restkey,
                                       params.restval,
                                       params.dialect,
                                       delimiter=params.delimiter,
                                       quotechar=params.quotechar,
                                       escapechar=params.escapechar,
                                       doublequote=params.doublequote,
                                       skipinitialspace=params.skipinitialspace,
                                       lineterminator=params.lineterminator,
                                       quoting=params.quoting,
                                       strict=params.strict)

            if params.rows == EnumDataClassFileCsvRows.FIRST:
                data_rows = [next(csv_reader)]
        except StopIteration as err:
            err.args = ("No hay filas en el Iterable CSV.",)
            raise err

        if params.rows == EnumDataClassFileCsvRows.ALL:
            data_rows = list(csv_reader)
        elif params.rows == EnumDataClassFileCsvRows.PARTIAL:
            if not params.partial_rows:
                err = "No se ha asignado un criterios en busqueda parcial de las filas CSV."
                raise TypeError(err)
            items = params.partial_rows.items()
            for row in csv_reader:
                is_row_select = all((v(row[k]) if callable(v) else row[k] == v for k, v in items))
                if is_row_select:
                    data_rows.append(row)

        csv_rows = [cls.from_dict(row) for row in data_rows]
        instance = cls()
        instance.__csv_rows__ = csv_rows
        return instance

    def to_csv(self, f: SupportsWrite[str], context: FileCSVContext, /) -> SupportsWrite[str]:
        """
        Converte las filas del CSV de un listado de diccionarios a un texto CSV.
        """
        params = context.onsave
        if len(self.__csv_rows__) == 0:
            return f
        csv_rows = [line.to_dict() for line in self.__csv_rows__]
        csv_writer = CsvDictWriter(f,
                                   params.fieldnames,
                                   params.restval,
                                   params.extrasaction,
                                   params.dialect,
                                   delimiter=params.delimiter,
                                   quotechar=params.quotechar,
                                   escapechar=params.escapechar,
                                   doublequote=params.doublequote,
                                   skipinitialspace=params.skipinitialspace,
                                   lineterminator=params.lineterminator,
                                   quoting=params.quoting,
                                   strict=params.strict)
        if params.hasfields:
            csv_writer.writeheader()
        if params.rows == EnumDataClassFileCsvRows.FIRST:
            csv_writer.writerow(csv_rows[0])
        elif params.rows == EnumDataClassFileCsvRows.ALL:
            csv_writer.writerows(csv_rows)
        else:
            if not params.partial_rows:
                err = "No se ha asignado un criterios en busqueda parcial de las filas CSV."
                raise TypeError(err)
            items = params.partial_rows.items()
            for row in csv_rows:
                is_row_select = all((v(row[k]) if callable(v) else row[k] == v for k, v in items))
                if is_row_select:
                    csv_writer.writerow(row)
        return f


    def onload_file(self, __file: TextIOWrapper, __context: FileContext, /) -> int:
        """
        Metodo de evento, util para definir comportamiento de la lectura de un archivo CSV
        antes del cierre automatico.

        Evento: al leer el archivo.

        :param __file: StreamIO del archivo al ejecutar la función `load_file`.
        :type __file: TextIOWrapper
        :param __context: Contexto del archivo en que se invoca el evento.
        :type __context: FileContext
        """
        try:
            new_csv_rows = list(self.__class__.from_csv(__file, __context))
            for row, new_row in zip(self.__csv_rows__, new_csv_rows):
                row.replace(new_row)
            len_difer = len(new_csv_rows) - len(self.__csv_rows__)

            if len_difer > 0:
                self.__csv_rows__.extend(new_csv_rows[-len_difer:])
            elif len_difer < 0:
                self.__csv_rows = self.__csv_rows__[0:-len_difer]

            self.setrow()
        except StopIteration as err:
            err.args = (f"No se cargó la primera fila del archivo CSV: '{__file.name}'",)
            raise err
        return 0

    def onsave_file(self, __file: TextIOWrapper, __context: FileContext, /) -> int:
        """
        Metodo de evento, util para definir comportamiento de la escritura de un archivo CSV
        antes del cierre automatico.

        Evento: al guardar el archivo.

        :param __file: StreamIO del archivo al ejecutar la función `save_file`.
        :type __file: TextIOWrapper
        :param __context: Contexto del archivo en que se invoca el evento.
        :type __context: FileContext
        :returns int: Número de estado de salida "exit status".
        """
        self.to_csv(__file, __context)
        return 0

    __iter_value = 0

    def __iter__(self):
        self.__iter_value = 0
        return self

    def __next__(self):
        if self.__iter_value == len(self.__csv_rows__):
            err = f"El numero de fila '{self.__iter_value}' está fuera del rango de las filas CSV."
            raise StopIteration(err)
        index = self.__iter_value
        self.__iter_value += 1
        return self.__csv_rows__[index]
