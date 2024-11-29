from src.data._file import DataFile, DataFileLocStatus as DFStatus
from pathlib import Path
from src.utils import WORKING_DIR

data_file = DataFile()
data_file.set_name("Compra 2021-02-14 08-00-00 FEV055555.csv")
data_file.set_location(WORKING_DIR / r"data\tests\pedido_de_compra\Almacenamiento")
data_file.set_location(WORKING_DIR / r"data\tests\pedido_de_compra\Entrada", DFStatus.OnHold)
data_file.set_location(WORKING_DIR / r"data\tests\pedido_de_compra\Rechazado", DFStatus.Reject)

def test_data_file():
  assert data_file.set_reader()
