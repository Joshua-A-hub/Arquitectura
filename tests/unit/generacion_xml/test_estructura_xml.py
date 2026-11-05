"""Estructura del documento UBL: raíz, namespaces, catálogos de cabecera y orden del XSD.

Esta parte no depende de una regla de negocio: verifica que el documento cumpla la
*forma* que exige el estándar (catálogos 01, 02, 03 y 51; orden de elementos).
Trazabilidad: matriz filas 1 a 13 y 26 a 34.
"""

from __future__ import annotations

import pytest
from lxml import etree

from src.adaptadores.salida.ubl import NAMESPACES
from src.dominio.catalogos import UnidadMedida
from tests.unit.generacion_xml import escenarios as f


@pytest.mark.parametrize(
    ("escenario", "raiz_ubl"),
    [
        ("factura-contrato", "Invoice"),
        ("boleta-dni", "Invoice"),
        ("factura-exportacion", "Invoice"),
        ("nota-credito-devolucion", "CreditNote"),
    ],
)
def test_el_tipo_del_dominio_elige_el_documento_ubl(escenario: str, raiz_ubl: str) -> None:
    xml = f.arbol(f.ESCENARIOS[escenario]())
    assert etree.QName(xml).localname == raiz_ubl
    assert etree.QName(xml).namespace == NAMESPACES[raiz_ubl]


def test_la_nota_de_debito_usa_el_documento_debit_note() -> None:
    xml = f.arbol(f.nota_debito_por_intereses())
    assert etree.QName(xml).localname == "DebitNote"
    assert etree.QName(xml).namespace == NAMESPACES["DebitNote"]


def test_version_ubl_21_y_personalizacion_sunat() -> None:
    xml = f.arbol(f.factura_del_contrato())
    assert f.texto(xml, "cbc:UBLVersionID") == "2.1"
    assert f.texto(xml, "cbc:CustomizationID") == "2.0"
    assert f.texto(xml, "cbc:CustomizationID/@schemeAgencyName") == "PE:SUNAT"


@pytest.mark.parametrize(
    ("escenario", "codigo", "operacion"),
    [
        ("factura-contrato", "01", "0101"),
        ("boleta-dni", "03", "0101"),
        ("factura-exportacion", "01", "0200"),
    ],
)
def test_tipo_de_comprobante_catalogo_01_y_operacion_catalogo_51(
    escenario: str, codigo: str, operacion: str
) -> None:
    xml = f.arbol(f.ESCENARIOS[escenario]())
    assert f.texto(xml, "cbc:InvoiceTypeCode") == codigo
    assert f.texto(xml, "cbc:InvoiceTypeCode/@listID") == operacion
    assert f.texto(xml, "cbc:InvoiceTypeCode/@listURI").endswith("catalogo01")


@pytest.mark.parametrize(
    ("escenario", "moneda"), [("factura-contrato", "PEN"), ("factura-exportacion", "USD")]
)
def test_la_moneda_del_catalogo_02_aparece_en_todos_los_importes(escenario: str, moneda: str) -> None:
    xml = f.arbol(f.ESCENARIOS[escenario]())
    assert f.texto(xml, "cbc:DocumentCurrencyCode") == moneda
    assert set(f.todos(xml, "//@currencyID")) == {moneda}


def test_el_xml_declara_utf8() -> None:
    assert b'encoding="UTF-8"' in f.generar(f.factura_del_contrato())[:60]


def test_el_xml_se_genera_sin_firma() -> None:
    assert b"ext:UBLExtensions" not in f.generar(f.factura_con_isc_de_tres_sistemas())


def test_dos_generaciones_del_mismo_comprobante_son_identicas() -> None:
    assert f.generar(f.factura_con_isc_de_tres_sistemas()) == f.generar(f.factura_con_isc_de_tres_sistemas())


@pytest.mark.parametrize(
    ("unidad", "codigo"),
    [
        (UnidadMedida.UNIDAD, "NIU"),
        (UnidadMedida.KILOGRAMO, "KGM"),
        (UnidadMedida.CAJA, "BX"),
        (UnidadMedida.LITRO, "LTR"),
        (UnidadMedida.SERVICIO, "ZZ"),
        (UnidadMedida.SACO, "SA"),
    ],
)
def test_unidad_de_medida_catalogo_03(unidad: UnidadMedida, codigo: str) -> None:
    xml = f.arbol(f.armar(f.TipoComprobante.FACTURA, "F001", (f.linea(1, unidad=unidad),)))
    assert f.texto(xml, "cac:InvoiceLine/cbc:InvoicedQuantity/@unitCode") == codigo


def test_orden_de_los_elementos_de_la_linea_segun_el_xsd() -> None:
    """El XSD impone el orden: ID, cantidad, importe, PricingReference, TaxTotal, Item, Price."""
    xml = f.arbol(f.factura_del_contrato())
    linea = xml.xpath("cac:InvoiceLine", namespaces=f.NS)[0]
    ns_cbc = NAMESPACES["cbc"]
    ns_cac = NAMESPACES["cac"]
    esperado = [
        f"{{{ns_cbc}}}ID",
        f"{{{ns_cbc}}}InvoicedQuantity",
        f"{{{ns_cbc}}}LineExtensionAmount",
        f"{{{ns_cac}}}PricingReference",
        f"{{{ns_cac}}}TaxTotal",
        f"{{{ns_cac}}}Item",
        f"{{{ns_cac}}}Price",
    ]
    assert [hijo.tag for hijo in linea] == esperado
