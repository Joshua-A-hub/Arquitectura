"""Fábrica de comprobantes del dominio para las pruebas.

Los escenarios salen de **nuestros** artefactos de la fase 1:

* la factura del contrato `F001-00000123` (S/ 530.00) de
  `specs/contracts/dto/ejemplo-comprobante.json` y `specs/ejemplos/emision-cli.json`;
* los productos del maestro de `tests/mocks/mock_db.py` (ISC de los tres sistemas);
* los casos de uso de `specs/features/casos-de-uso.md` (boleta, nota de crédito, migración).

Las pruebas parten SIEMPRE de objetos del dominio, nunca de JSON ni de HTTP: así se verifica la
traducción «lenguaje del dominio → UBL 2.1» de forma aislada.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal as D

from lxml import etree

from src.adaptadores.salida.ubl import NAMESPACES
from src.adaptadores.salida.ubl.generador import GeneradorUblXsdata
from src.dominio.catalogos import (
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
from src.dominio.comprobante import Cliente, Comprobante, Cuota, Emisor, FormaPago, Linea
from src.dominio.tributos import ConfiguracionISC
from src.dominio.valores import RUC, Correlativo, DocumentoIdentidad, Serie

# Datos del caso: fecha y hora del contrato de ejemplo.
HOY = dt.date(2026, 10, 22)
HORA = dt.time(9, 15, 0)

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
    "DISTRIBUIDORA SELVA SAC",
    direccion="AV. ARGENTINA 123",
    ubigeo="150101",
)
CLIENTE_DNI = Cliente(DocumentoIdentidad(TipoDocumentoIdentidad.DNI, "45678912"), "JUAN PEREZ GOMEZ")
CLIENTE_EXTERIOR = Cliente(
    DocumentoIdentidad(TipoDocumentoIdentidad.NO_DOMICILIADO, "US-99887766"), "GROCERY IMPORTS LLC"
)


def linea(
    numero: int,
    descripcion: str = "SACO DE ARROZ 50KG",
    *,
    cantidad: str = "10",
    precio: str = "45.00",
    unidad: UnidadMedida = UnidadMedida.UNIDAD,
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


# ------------------------------------------------------------------ escenarios del contrato
def factura_del_contrato() -> Comprobante:
    """La factura del contrato: F001-00000123, S/ 530.00 (valor 449.83 + IGV 70.17 + ICBPER 10.00)."""
    return armar(
        TipoComprobante.FACTURA,
        "F001",
        (
            linea(1, "SACO DE ARROZ 50KG", cantidad="10", precio="45.00", codigo="ARR-50KG"),
            linea(
                2,
                "CAJA DE LECHE 1L",
                cantidad="5",
                precio="12.00",
                unidad=UnidadMedida.CAJA,
                codigo="LEC-1L",
                afectacion=AfectacionIGV.EXONERADO_ONEROSA,
            ),
            linea(
                3,
                "BOLSA PLASTICA RECICLABLE",
                cantidad="20",
                precio="0.50",
                codigo="BOL-001",
                icbper=True,
            ),
        ),
        correlativo=123,
    )


def factura_con_isc_de_tres_sistemas() -> Comprobante:
    """ISC del catálogo 08 (01, 02 y 03) con productos del maestro del caso."""
    return armar(
        TipoComprobante.FACTURA,
        "FA01",
        (
            # Sistema 02: pisco, S/ 1.35 por unidad.
            linea(
                1,
                "PISCO QUEBRANTA 750 ML",
                cantidad="6",
                precio="53.10",
                codigo="PIS-750ML",
                isc=ConfiguracionISC(SistemaISC.MONTO_FIJO, monto_fijo=D("1.35")),
            ),
            # Sistema 01: cerveza al 25 %.
            linea(
                2,
                "CERVEZA BOTELLA 620 ML",
                cantidad="12",
                precio="8.00",
                codigo="CER-620ML",
                isc=ConfiguracionISC(SistemaISC.AD_VALOR, tasa=D("0.25")),
            ),
            # Sistema 03: gaseosa, precio de venta al público S/ 12.50.
            linea(
                3,
                "GASEOSA 3 L",
                cantidad="4",
                precio="10.62",
                codigo="GAS-3L",
                isc=ConfiguracionISC(
                    SistemaISC.PRECIO_VENTA_PUBLICO, tasa=D("0.17"), precio_venta_publico=D("12.50")
                ),
            ),
            linea(
                4,
                "BOLSA PLASTICA RECICLABLE",
                cantidad="3",
                precio="0.50",
                codigo="BOL-001",
                icbper=True,
            ),
            linea(
                5,
                "LIBRO ESCOLAR",
                cantidad="2",
                precio="30.00",
                codigo=None,
                afectacion=AfectacionIGV.EXONERADO_ONEROSA,
            ),
            linea(
                6,
                "FLETE INTERNO",
                cantidad="1",
                precio="15.00",
                unidad=UnidadMedida.SERVICIO,
                codigo=None,
                afectacion=AfectacionIGV.INAFECTO_ONEROSA,
            ),
        ),
    )


def factura_de_exportacion() -> Comprobante:
    """Exportación en USD a cliente no domiciliado (catálogo 06 = 0)."""
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


def boleta_con_dni() -> Comprobante:
    """Boleta a cliente con DNI (caso de uso de venta al detalle)."""
    return armar(
        TipoComprobante.BOLETA,
        "B001",
        (
            linea(
                1,
                "ACEITE VEGETAL BOTELLA 1 L",
                cantidad="2",
                precio="8.50",
                codigo="ACE-001",
            ),
        ),
        cliente=CLIENTE_DNI,
    )


def nota_credito_por_devolucion() -> Comprobante:
    """Nota de crédito que devuelve el ítem completo de la factura del contrato (CU de notas)."""
    return armar(
        TipoComprobante.NOTA_CREDITO,
        "FC01",
        (linea(1, "SACO DE ARROZ 50KG", cantidad="10", precio="45.00", codigo="ARR-50KG"),),
        referencia=factura_del_contrato(),
        motivo=MotivoNotaCredito.DEVOLUCION_ITEM,
    )


def factura_migrada_con_vale() -> Comprobante:
    """Factura que conserva el vale informal del legado como documento relacionado (RN-23)."""
    return armar(
        TipoComprobante.FACTURA,
        "F003",
        (linea(1, "AZUCAR RUBIA", cantidad="250", precio="3.80", codigo="AZU-001"),),
        documentos_legado=("VALE-SALIDA-0042",),
    )


# ------------------------------------------------------------------ escenarios auxiliares
def factura_al_credito() -> Comprobante:
    """Factura del contrato pagada en dos cuotas (RS 193-2020)."""
    cuotas = (Cuota(D("265.00"), dt.date(2026, 11, 21)), Cuota(D("265.00"), dt.date(2026, 12, 21)))
    base = factura_del_contrato()
    return armar(
        TipoComprobante.FACTURA,
        base.serie.valor,
        base.lineas,
        correlativo=124,
        forma_pago=FormaPago(TipoFormaPago.CREDITO, cuotas),
    )


def nota_debito_por_intereses() -> Comprobante:
    """Nota de débito por intereses moratorios (catálogo 10)."""
    return armar(
        TipoComprobante.NOTA_DEBITO,
        "FD01",
        (
            linea(
                1,
                "INTERESES MORATORIOS",
                cantidad="1",
                precio="15.00",
                unidad=UnidadMedida.SERVICIO,
                codigo=None,
                afectacion=AfectacionIGV.GRAVADO_ONEROSA,
            ),
        ),
        referencia=factura_del_contrato(),
        motivo=MotivoNotaDebito.INTERESES_MORA,
    )


#: Escenarios con XML de referencia en `esperados/`: los cinco del caso más la exportación.
ESCENARIOS = {
    "factura-contrato": factura_del_contrato,
    "factura-isc-tres-sistemas": factura_con_isc_de_tres_sistemas,
    "factura-exportacion": factura_de_exportacion,
    "boleta-dni": boleta_con_dni,
    "nota-credito-devolucion": nota_credito_por_devolucion,
    "factura-migrada-vale": factura_migrada_con_vale,
}


# ------------------------------------------------------------------ utilidades
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
