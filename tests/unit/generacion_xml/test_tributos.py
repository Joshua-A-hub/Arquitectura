"""Taller 2 · Generación: tributos (IGV, ISC de los tres sistemas, ICBPER) y cuadre."""

from __future__ import annotations

import re

import pytest

from tests.unit.generacion_xml import fabrica as f

LINEA = "cac:InvoiceLine[{n}]"


def _subtotal(n: int, i: int) -> str:
    return f"{LINEA.format(n=n)}/cac:TaxTotal/cac:TaxSubtotal[{i}]"


def test_igv_de_una_linea_gravada() -> None:
    xml = f.arbol(f.factura_contado())
    sub = _subtotal(1, 1)
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cbc:Percent") == "18.00"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cbc:TaxExemptionReasonCode") == "10"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cac:TaxScheme/cbc:ID") == "1000"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cac:TaxScheme/cbc:Name") == "IGV"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode") == "VAT"
    assert f.texto(xml, f"{sub}/cbc:TaxAmount") == "32.03"


@pytest.mark.parametrize(
    ("linea", "tributo", "afectacion"),
    [(6, "9997", "20"), (7, "9998", "30")],
)
def test_lineas_exonerada_e_inafecta_no_generan_igv(linea: int, tributo: str, afectacion: str) -> None:
    xml = f.arbol(f.factura_completa())
    sub = _subtotal(linea, 1)
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cac:TaxScheme/cbc:ID") == tributo
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cbc:TaxExemptionReasonCode") == afectacion
    assert f.texto(xml, f"{sub}/cbc:TaxAmount") == "0.00"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cbc:Percent") == "0.00"


def test_exportacion_usa_el_tributo_9995() -> None:
    xml = f.arbol(f.factura_exportacion_usd())
    sub = _subtotal(1, 1)
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cac:TaxScheme/cbc:ID") == "9995"
    assert f.texto(xml, f"{sub}/cbc:TaxAmount") == "0.00"


# --- ISC: catálogo 08, tres sistemas -------------------------------------------------


def test_isc_sistema_01_ad_valorem_con_tier_range() -> None:
    xml = f.arbol(f.factura_completa())  # línea 3: cerveza, sistema 01, tasa 25 %
    sub = _subtotal(3, 1)
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cbc:TierRange") == "01"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cbc:Percent") == "25.00"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cac:TaxScheme/cbc:ID") == "2000"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cac:TaxScheme/cbc:Name") == "ISC"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode") == "EXC"
    assert f.texto(xml, f"{sub}/cbc:TaxAmount") == "20.34"


def test_isc_sistema_02_especifico_con_per_unit_amount() -> None:
    xml = f.arbol(f.factura_completa())  # línea 2: pisco, sistema 02, S/ 1.35 por unidad
    sub = _subtotal(2, 1)
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cbc:TierRange") == "02"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cbc:PerUnitAmount") == "1.35"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cac:TaxScheme/cbc:ID") == "2000"
    # 6 unidades x 1.35 = 8.10
    assert f.texto(xml, f"{sub}/cbc:TaxAmount") == "8.10"


def test_isc_sistema_03_al_valor_con_tier_range() -> None:
    xml = f.arbol(f.factura_completa())  # línea 4: gaseosa, sistema 03
    sub = _subtotal(4, 1)
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cbc:TierRange") == "03"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cac:TaxScheme/cbc:ID") == "2000"


def test_la_base_del_igv_de_la_linea_incluye_el_isc() -> None:
    """Regla SUNAT 3108: en la línea, base del IGV = valor de venta + ISC."""
    xml = f.arbol(f.factura_completa())  # cerveza: valor 81.36, ISC 20.34, base 101.70
    igv = _subtotal(3, 2)
    assert f.texto(xml, f"{igv}/cbc:TaxableAmount") == "101.70"
    assert f.texto(xml, f"{igv}/cbc:TaxAmount") == "18.31"


def test_la_base_global_del_igv_no_incluye_el_isc() -> None:
    """Regla SUNAT 3277: la base global del IGV es el valor de venta, sin ISC."""
    comprobante = f.factura_completa()
    xml = f.arbol(comprobante)
    tax_totales = xml.xpath("cac:TaxTotal", namespaces=f.NS)
    igv = next(
        t for t in tax_totales
        if t.findtext("cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID", namespaces=f.NS) == "1000"
    )
    base = igv.findtext("cac:TaxSubtotal/cbc:TaxableAmount", namespaces=f.NS)
    assert base == f"{comprobante.totales.op_gravada:.2f}"
    valor_venta = xml.findtext("cac:LegalMonetaryTotal/cbc:LineExtensionAmount", namespaces=f.NS)
    assert base != valor_venta  # el ISC está en la línea pero no en la base global


# --- ICBPER -------------------------------------------------------------------------


def test_icbper_con_monto_por_unidad_y_unidad_de_medida() -> None:
    xml = f.arbol(f.factura_completa())  # línea 5: 3 bolsas
    sub = _subtotal(5, 2)
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cac:TaxScheme/cbc:ID") == "7152"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cbc:PerUnitAmount") == "0.50"
    assert f.texto(xml, f"{sub}/cbc:BaseUnitMeasure") == "3"
    assert f.texto(xml, f"{sub}/cbc:TaxAmount") == "1.50"


# --- cuadre -------------------------------------------------------------------------


def test_el_tax_total_de_la_linea_suma_sus_tributos() -> None:
    xml = f.arbol(f.factura_completa())
    # cerveza: ISC 20.34 + IGV 18.31
    assert f.texto(xml, f"{LINEA.format(n=3)}/cac:TaxTotal/cbc:TaxAmount") == "38.65"


def test_el_documento_declara_un_tax_total_por_tributo() -> None:
    xml = f.arbol(f.factura_completa())
    codigos = f.todos(xml, "cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID")
    assert codigos == ["1000", "2000", "9997", "9998", "7152"]


def test_el_total_de_impuestos_del_documento_cuadra() -> None:
    xml = f.arbol(f.factura_completa())
    total = xml.findtext("cac:TaxTotal/cbc:TaxAmount", namespaces=f.NS)
    subtotales = f.todos(xml, "cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount")
    assert f"{sum(map(float, subtotales)):.2f}" == total


def test_todos_los_importes_llevan_dos_decimales() -> None:
    xml = f.arbol(f.factura_completa())
    importes = f.todos(xml, "//cbc:TaxAmount") + f.todos(xml, "//cbc:TaxableAmount")
    assert importes
    for importe in importes:
        assert re.fullmatch(r"-?\d+\.\d{2}", importe), f"importe sin 2 decimales: {importe}"


def test_la_exportacion_declara_su_subtotal_en_el_documento() -> None:
    xml = f.arbol(f.factura_exportacion_usd())
    sub = "cac:TaxTotal/cac:TaxSubtotal[1]"
    assert f.texto(xml, f"{sub}/cac:TaxCategory/cac:TaxScheme/cbc:ID") == "9995"
    assert f.texto(xml, f"{sub}/cbc:TaxableAmount") == "2100.00"
    assert f.texto(xml, f"{sub}/cbc:TaxAmount") == "0.00"
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:PayableAmount") == "2100.00"
