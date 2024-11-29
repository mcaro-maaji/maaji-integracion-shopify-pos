"""TODO: DOCS"""

import json
from typing import Optional
from os import environ
from datetime import datetime
from dataclasses import dataclass, field
from .dataclass import DataClass, config

@dataclass
class DataApiCredentials(DataClass):
    grant_type: Optional[str] = environ.get("DYNAMICS_SERVICE_AUTH_GRANTYPE")
    aad_tenant: Optional[str] = environ.get("DYNAMICS_SERVICE_AAD_TENANT")
    client_id: Optional[str] = environ.get("DYNAMICS_SERVICE_CLIENT_ID")
    client_secret: Optional[str] = environ.get("DYNAMICS_SERVICE_CLIENT_SECRET")
    resource: str = ""

    def exists(self) -> bool:
        """Comprueba si existen las credenciales del servicio."""
        return all((
            self.grant_type is not None,
            self.aad_tenant is not None,
            self.client_id is not None,
            self.client_secret is not None
        ))

@dataclass
class DataApiAuthentication(DataClass):
    token_type: str = ""
    expires_in: str = ""
    ext_expires_in: str = ""
    expires_on: datetime = field(
                                default_factory=datetime.now,
                                metadata=config(decoder=lambda v: datetime.fromtimestamp(float(v))))
    not_before: datetime = field(
                                default_factory=datetime.now,
                                metadata=config(decoder=lambda v: datetime.fromtimestamp(float(v))))
    resource: str = ""
    access_token: str = ""

@dataclass
class DataApiPayload(DataClass):
    DataAreaId: str
    FecIni: datetime
    FecFin: datetime

@dataclass
class DataApiResService(DataClass):
    id: str = field(default="", metadata=config(field_name="$id"))
    ErrorMessage: str = ""
    Success: bool = False
    DebugMessage: list[dict] = field(default_factory=list, metadata=config(decoder=json.loads))

@dataclass
class DataApiServiceBills(DataClass):
    id_integracion: str = ""
    numero_factura: str = ""
    fecha_factura: str = ""
    tienda: str = ""
    almacen_tienda: str = ""
    proveedor: str = ""
    ean: str = ""
    cantidad: str = ""
    costo_compra: str = ""
    moneda: str = ""
    factura: str = ""

@dataclass
class DataApiServicePrices(DataClass):
    id: str = ""
    moneda: str = ""
    codigo: str = ""
    ean: str = ""
    copRP: str = ""
    fecha_modificacion: str = ""

@dataclass
class DataApiServiceProducts(DataClass):
    CodigCegidArticulos: str = ""
    referenciaProducto: str = ""
    codigoAlternoProducto: str = ""
    nombreLargoProducto: str = ""
    nombreCortoProducto: str = ""
    codigoBarrasProducto: str = ""
    proveedorPrincipal: str = ""
    mascaraDimension: str = ""
    dimension: str = ""
    codigoAlternoTalla: str = ""
    nombre1Talla: str = ""
    dimension2: str = ""
    codigoAlternoColor: str = ""
    nombre1Color: str = ""
    codigoAlternoTemporada: str = ""
    nombreTemporada: str = ""
    cod_grupo: str = ""
    grupo: str = ""
    lineaseccion_COD: str = ""
    lineaseccion_NOMBRE: str = ""
    codigoAlterno1Categoria: str = ""
    DescAlterno1Categoria: str = ""
    codigoAlterno2Categoria: str = ""
    DescAlterno2Categoria: str = ""
    codigoAlterno3Categoria: str = ""
    DescAlterno3Categoria: str = ""
    codigoAlterno4Categoria: str = ""
    DescAlterno4Categoria: str = ""
    codClienteObjetivo: str = ""
    desClienteObjetivo: str = ""
    codigoAlternoTipoNegocio: str = ""
    nombreTipoNegocio: str = ""
    codigoAlternoMarca: str = ""
    nombreMarca: str = ""
    codEvento: str = ""
    desEvento: str = ""
    codigoAlternoPais: str = ""
    nombrePais: str = ""
    codigoAlternoTipoProducto: str = ""
    nombreTipoProducto: str = ""
    familiaTasa1Articulo: str = ""
    precioDetalleImpuestoIncl: str = ""
    estadoProducto: str = ""
    estadoConservacion: str = ""
    fechaCreacionProducto: str = ""
    conceptoProducto: str = ""
    codDIFUSION: str = ""
    DescDIFUSION: str = ""
    codESTRATEGIA: str = ""
    descESTRATEGIA: str = ""
    fechaInicioEvento: str = ""
    fechaFinEvento: str = ""
    nombre2Talla: str = ""
    nombre3Talla: str = ""
    codigoAlternoTallaComplemento: str = ""
    nombre1TallaComplemento: str = ""
    nombre2TallaComplemento: str = ""
    nombre3TallaComplemento: str = ""
    nombre2Color: str = ""
    calificacionEstadoConservacion: str = ""
    fechaInicialTemporada: str = ""
    fechaFinalTemporada: str = ""
    codigoAlternoComposicion: str = ""
    nombreComposicion: str = ""
    altoProducto: str = ""
    anchoProducto: str = ""
    profundidadProducto: str = ""
    pesoBrutoProducto: str = ""
    pesoNetoProducto: str = ""
    codigoAlternoPosicionArancelaria: str = ""
    observacionesPosicionArancelaria: str = ""
    devolucionEntregaProductoDescripcion: str = ""
    cuidadoProductoDescripcion: str = ""
    descripcionOnlineProductoDescripcion: str = ""
    fitProductoDescripcion: str = ""
    ESTRATEGIAusa: str = ""
    seccionusa: str = ""
    eventousa: str = ""
    clienteobjetivousa: str = ""
    nombre1Colorusa: str = ""
    nombre2colorusa: str = ""
    codigoAlterno1Categoriausa: str = ""
    DescAlterno1Categoriausa: str = ""
    codigoAlterno2Categoriausa: str = ""
    DescAlterno2Categoriausa: str = ""
    codigoAlterno3Categoriausa: str = ""
    DescAlterno3Categoriausa: str = ""
    codigoAlterno4Categoriausa: str = ""
    DescAlterno4Categoriausa: str = ""
    nombreTemporadausa: str = ""
    nombreComposicionusa: str = ""
    devolucionEntregaProductoDescripcionusa: str = ""
    cuidadoProductoDescripcionusa: str = ""
    descripcionOnlineProductoDescripcionusa: str = ""
    fitProductoDescripcionusa: str = ""
    imagenproductofusion1: str = ""
    iva: str = ""
    fechaCreacion: str = ""
    imagen: str = ""
    imagen2: str = ""
    imagen3: str = ""
    imagen4: str = ""
