"""TODO: DOCS"""

from typing import Callable
from dataclasses import dataclass, field
from .data.dataclass import DataClass, DataClassFileJson, FileJSONContext, MetaDataClassFile
from .utils import WORKING_DIR

@dataclass
class AbsFields(DataClass):
    """Clase abstracta para los campos."""
    id: int


CEGID_DEPOTS = ("CE", "CA", "EC", "EX", "RB")
def cegidcodes(code: str):
    """Obtiene todas las bodegas de cegid, CE + code == CE001."""
    return [code, *list(map(lambda x: x+code, CEGID_DEPOTS))]

def cegidrange(codes: list[str], end: int, start=1) -> list[str]:
    """..."""
    range_num = list(range(start, end))
    depots = []
    for depot in codes:
        depots.extend(list(map(lambda x: depot + str(x), range_num)))
    return depots

@dataclass
class Stores(DataClass):
    """Homologación de campos de las tiendas."""
    @dataclass
    class Fields(AbsFields):
        """Campos de las tiendas."""
        names: list[str] = field(default_factory=lambda: [])
        codes: list[str] = field(default_factory=lambda: [])

    shopify: tuple[Fields] = (
        Fields(id=1, names=["Unidad Industrial Vegas de Sabaneta"]),
        Fields(id=2, names=["Zona Franca Rionegro", "ZN", "Vereda Chachafruto Zona Franca"]),
        Fields(id=3, names=["MAAJI MAYORCA OULET", "Tienda Mayorca"]),
        Fields(id=4, names=["MAAJI MONTERIA", "Tienda Montaria"])
    )
    dynamics: tuple[Fields] = (
        Fields(id=3, names=["MAAJI MAYORCA OULET", "Tienda Mayorca"]),
        Fields(id=4, names=["MAAJI MONTERIA", "Tienda Montaria"])
    )

    cegid_y2: tuple[Fields] = (
        Fields(id=3, names=["MAAJI MAYORCA OULET", "CEDI MAYORCA OUTLET"],
               codes=cegidrange(["CE"], 621, 600)),
        Fields(id=5, names=["ART MODE S.A.S"], codes=["501"]),
        Fields(id=6, names=["MAS S.A.S"], codes=["600"]),
        Fields(id=7, names=["ART MODE DEVOLUCIONES ECOMMERCE"], codes=["601"]),
        Fields(id=8, names=["MAAJI EL TESORO MEDELLÍN"], codes=[*cegidcodes("001"), "602"]),
        Fields(id=9, names=["MAAJI EL RETIRO BOGOTA"], codes=[*cegidcodes("002"), "603"]),
        Fields(id=10, names=["MAAJI SANTO DOMINGO CARTAGENA"], codes=[*cegidcodes("003"), "604"]),
        Fields(id=11, names=["MAAJI VIVA BARRANQUILLA"], codes=cegidcodes("005")),
        Fields(id=12, names=["MAAJI UNICENTRO CALI"], codes=[*cegidcodes("006"), "605"]),
        Fields(id=13, names=["MAAJI BOCAGRANDE CARTAGENA"], codes=[*cegidcodes("007"), "606"]),
        Fields(id=14, names=["MAAJI SANTAFE MEDELLIN"], codes=[*cegidcodes("008"), "607"]),
        Fields(id=15, names=["MAAJI CACIQUE BUCARAMANGA"], codes=cegidcodes("009")),
        Fields(id=16, names=["MAAJI UNICENTRO BOGOTA"], codes=[*cegidcodes("012"), "608"]),
        Fields(id=17, names=["MAAJI SERREZUELA CARTAGENA"], codes=[*cegidcodes("013"), "609"]),
        Fields(id=18, names=["MAAJI BUENAVISTA BARRANQUILLA"], codes=[*cegidcodes("014"), "610"]),
    )

    def find_by(self, predicate: Callable[[Fields], bool]):
        """Busca los campos de las tiendas según la función."""
        shopify_items = tuple(filter(predicate, self.shopify))
        dynamics_items = tuple(filter(predicate, self.dynamics))
        cegid_y2_items = tuple(filter(predicate, self.cegid_y2))
        list_ids = [*[item.id for item in shopify_items],
                    *[item.id for item in dynamics_items],
                    *[item.id for item in cegid_y2_items]]
        list_ids = set(list_ids)
        shopify_items = tuple(filter(lambda x: x.id in list_ids, self.shopify))
        dynamics_items = tuple(filter(lambda x: x.id in list_ids, self.dynamics))
        cegid_y2_items = tuple(filter(lambda x: x.id in list_ids, self.cegid_y2))
        return Stores(shopify=shopify_items, dynamics=dynamics_items, cegid_y2=cegid_y2_items)

@dataclass
class FieldMappingFile(DataClassFileJson):
    """
    Estructura base de la homologación de campos entre los sistemas integrados.
    """
    # Metadatos visibles en el archivo JSON
    __metadata__: MetaDataClassFile = field(default_factory=lambda: MetaDataClassFile(True))

    stores: Stores = field(default_factory=Stores)

FieldMapping = FieldMappingFile()
FieldMapping.setpath(WORKING_DIR / "fieldsmapping.json")
FieldMappingContext = FileJSONContext(onsave=FileJSONContext.OnSave(indent=4))
FieldMapping.setcontext(FieldMappingContext)
# FieldMapping.load_file() # TODO: Hacer configurables los campos
FieldMapping.save_file()
