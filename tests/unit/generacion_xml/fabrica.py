"""Fábrica de comprobantes del dominio para las pruebas de generación.

Las pruebas parten SIEMPRE de objetos del dominio (`Comprobante`), nunca de JSON ni de HTTP:
así se verifica la traducción «lenguaje del dominio → UBL 2.1» de forma aislada.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal as D

from lxml import etree

from src.adapters.outbound.ubl import NAMESPACES
from src.adapters.outbound.ubl.generador import GeneradorUblXsdata
from src.domain.catalogos import (
    AfectacionIGV,
    Moneda,
    MotivoNotaCredito,
    MotivoNotaDebito,
    SistemaISC,
    TipoComprobante,
    TipoDocumentoIdentidad,
    TipoFormaPago,
    TipoOperacion,
    UnidadMedida,
)
from src.domain.comprobante import Cliente, Comprobante, Cuota, Emisor, FormaPago, Linea
from src.domain.tributos import ConfiguracionISC
from src.domain.valores import RUC, Correlativo, DocumentoIdentidad, Serie

HOY = dt.date(2026, 10, 22)
HORA = dt.time(10, 30, 0)

NS = {clave: valor for clave, valor in NAMESPACES.items() if clave in ("cac", "cbc")}

EMISOR = Emisor(
    ruc=RUC("20123456786"),
    razon_social="ABC SOFTWARE CORP SAC",
    nombre_comercial="ABC Abarrotes",
    ubigeo="150101",
    direccion="AV. COLONIAL 456",
)

CLIENTE_RUC = Cliente(
    DocumentoIdentidad(TipoDocumentoIdentidad.RUC, "20512345671"),
    "DISTRIBUIDORA EL SOL & CIA S.A.C.",
    direccion="JR. COMERCIO 123, LIMA",
)
CLIENTE_DNI = Cliente(DocumentoIdentidad(TipoDocumentoIdentidad.DNI, "45678912"), "MARÍA QUISPE HUAMÁN")
CLIENTE_EXTERIOR = Cliente(
    DocumentoIdentidad(TipoDocumentoIdentidad.NO_DOMICILIADO, "US-99887766"), "GROCERY IMPORTS LLC"
)


def linea(
    numero: int,
    descripcion: str = "SACO DE ARROZ 50KG",
    *,
    cantidad: str = "50",
    precio: str = "4.20",
    unidad: UnidadMedida = UnidadMedida.KILOGRAMO,
    afectacion: AfectacionIGV = AfectacionIGV.GRAVADO_ONEROSA,
    codigo: str | None = "ARR-50KG",
    isc: ConfiguracionISC | None = None,
    icbper: bool = False,
) -> Linea:
    return Linea.calcular(
        numero=numero,
        descripcion=descripcion,
        unidad=unidad,
        cantidad=cantidad,
        precio_unitario=precio,
        afectacion=afectacion,
        codigo_producto=codigo,
        isc=isc,
        aplica_icbper=icbper,
    )


def armar(
    tipo: TipoComprobante,
    serie: str,
    lineas: tuple[Linea, ...],
    *,
    cliente: Cliente = CLIENTE_RUC,
    correlativo: int = 1,
    moneda: Moneda = Moneda.PEN,
    tipo_operacion: TipoOperacion = TipoOperacion.VENTA_INTERNA,
    forma_pago: FormaPago | None = None,
    referencia: Comprobante | None = None,
    motivo=None,
    documentos_legado: tuple[str, ...] = (),
) -> Comprobante:
    return Comprobante(
        tipo=tipo,
        serie=Serie(serie),
        correlativo=Correlativo(correlativo),
        fecha_emision=HOY,
        hora_emision=HORA,
        emisor=EMISOR,
        cliente=cliente,
        lineas=lineas,
        moneda=moneda,
        tipo_operacion=tipo_operacion,
        forma_pago=forma_pago,
        referencia=referencia,
        motivo=motivo,
        sustento="Sustento de la nota" if motivo else None,
        documentos_legado=documentos_legado,
    )


# ---------------------------------------------------------------- escenarios
def factura_contado() -> Comprobante:
    return armar(TipoComprobante.FACTURA, "F001", (linea(1),))


def factura_credito() -> Comprobante:
    # 50 kg x 4.20 (precio con IGV) = 210.00, en dos cuotas de 105.00.
    cuotas = (Cuota(D("105.00"), dt.date(2026, 11, 21)), Cuota(D("105.00"), dt.date(2026, 12, 21)))
    return armar(
        TipoComprobante.FACTURA,
        "F001",
        (linea(1),),
        forma_pago=FormaPago(TipoFormaPago.CREDITO, cuotas),
    )


def factura_completa() -> Comprobante:
    """Una línea por cada caso tributario: gravado, ISC 01/02/03, ICBPER, exonerado e inafecto."""
    return armar(
        TipoComprobante.FACTURA,
        "FA01",
        (
            linea(1),
            linea(
                2,
                "PISCO QUEBRANTA 750 ML",
                cantidad="6",
                precio="53.10",
                unidad=UnidadMedida.UNIDAD,
                codigo="PIS-750ML",
                isc=ConfiguracionISC(SistemaISC.MONTO_FIJO, monto_fijo=D("1.35")),
            ),
            linea(
                3,
                "CERVEZA BOTELLA 620 ML",
                cantidad="12",
                precio="8.00",
                unidad=UnidadMedida.UNIDAD,
                codigo="CER-620ML",
                isc=ConfiguracionISC(SistemaISC.AD_VALOR, tasa=D("0.25")),
            ),
            linea(
                4,
                "GASEOSA 3 L",
                cantidad="4",
                precio="10.62",
                unidad=UnidadMedida.UNIDAD,
                codigo="GAS-3L",
                isc=ConfiguracionISC(SistemaISC.PRECIO_VENTA_PUBLICO, tasa=D("0.17"), precio_venta_publico=D("12.50")),
            ),
            linea(
                5,
                "BOLSA PLASTICA RECICLABLE",
                cantidad="3",
                precio="0.50",
                unidad=UnidadMedida.UNIDAD,
                codigo="BOL-001",
                icbper=True,
            ),
            linea(
                6,
                "LIBRO ESCOLAR",
                cantidad="2",
                precio="30.00",
                unidad=UnidadMedida.UNIDAD,
                codigo=None,
                afectacion=AfectacionIGV.EXONERADO_ONEROSA,
            ),
            linea(
                7,
                "FLETE INTERNO",
                cantidad="1",
                precio="15.00",
                unidad=UnidadMedida.SERVICIO,
                codigo=None,
                afectacion=AfectacionIGV.INAFECTO_ONEROSA,
            ),
        ),
    )


def factura_exportacion_usd() -> Comprobante:
    return armar(
        TipoComprobante.FACTURA,
        "F002",
        (
            linea(
                1,
                "QUINUA BLANCA",
                cantidad="1000",
                precio="2.10",
                unidad=UnidadMedida.KILOGRAMO,
                afectacion=AfectacionIGV.EXPORTACION,
                codigo=None,
            ),
        ),
        cliente=CLIENTE_EXTERIOR,
        moneda=Moneda.USD,
        tipo_operacion=TipoOperacion.EXPORTACION,
    )


def factura_de_vale() -> Comprobante:
    return armar(
        TipoComprobante.FACTURA,
        "F001",
        (linea(1, "AZUCAR RUBIA", cantidad="250", precio="3.80", codigo="AZU-001"),),
        documentos_legado=("VALE-SALIDA-0042",),
    )


def boleta() -> Comprobante:
    return armar(
        TipoComprobante.BOLETA,
        "B001",
        (
            linea(
                1,
                "ACEITE VEGETAL BOTELLA 1 L",
                cantidad="2",
                precio="8.50",
                unidad=UnidadMedida.UNIDAD,
                codigo="ACE-001",
            ),
        ),
        cliente=CLIENTE_DNI,
    )


def nota_credito() -> Comprobante:
    return armar(
        TipoComprobante.NOTA_CREDITO,
        "FC01",
        (linea(1, cantidad="10"),),
        referencia=factura_contado(),
        motivo=MotivoNotaCredito.DEVOLUCION_ITEM,
    )


def nota_debito() -> Comprobante:
    return armar(
        TipoComprobante.NOTA_DEBITO,
        "FD01",
        (linea(1, "INTERESES MORATORIOS", cantidad="1", precio="15.00", unidad=UnidadMedida.SERVICIO, codigo=None),),
        referencia=factura_contado(),
        motivo=MotivoNotaDebito.INTERESES_MORA,
    )


ESCENARIOS = {
    "factura-contado": factura_contado,
    "factura-credito": factura_credito,
    "factura-completa": factura_completa,
    "factura-exportacion-usd": factura_exportacion_usd,
    "factura-de-vale": factura_de_vale,
    "boleta": boleta,
    "nota-credito": nota_credito,
    "nota-debito": nota_debito,
}


# ---------------------------------------------------------------- utilidades
def generar(c: Comprobante) -> bytes:
    return GeneradorUblXsdata().generar(c)


def arbol(c: Comprobante) -> etree._Element:
    return etree.fromstring(generar(c))


def texto(raiz: etree._Element, xpath: str) -> str:
    nodos = raiz.xpath(xpath, namespaces=NS)
    assert nodos, f"No existe {xpath}"
    nodo = nodos[0]
    return nodo if isinstance(nodo, str) else (nodo.text or "")


def todos(raiz: etree._Element, xpath: str) -> list[str]:
    return [n if isinstance(n, str) else (n.text or "") for n in raiz.xpath(xpath, namespaces=NS)]
