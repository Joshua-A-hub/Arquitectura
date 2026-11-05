"""RN-04 · Valor unitario sin IGV a partir del precio con IGV.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-04 · matriz filas 30 y 31
(`cac:Price/cbc:PriceAmount` y `cac:PricingReference/.../cbc:PriceAmount`).
"""

from __future__ import annotations

from decimal import Decimal

from src.dominio.catalogos import AfectacionIGV
from src.dominio.tributos import valor_unitario
from tests.unit.generacion_xml import fabrica as f

LINEA = "cac:InvoiceLine"


def test_el_valor_unitario_gravado_descuenta_el_igv() -> None:
    assert valor_unitario(Decimal("118.00"), AfectacionIGV.GRAVADO_ONEROSA) == Decimal("100")


def test_el_valor_unitario_exonerado_no_descuenta_igv() -> None:
    assert valor_unitario(Decimal("118.00"), AfectacionIGV.EXONERADO_ONEROSA) == Decimal("118.00")


def test_el_xml_declara_precio_con_igv_y_valor_sin_igv() -> None:
    xml = f.arbol(f.factura_contado())
    alternativa = f"{LINEA}/cac:PricingReference/cac:AlternativeConditionPrice"
    assert f.texto(xml, f"{alternativa}/cbc:PriceAmount") == "4.20"
    assert f.texto(xml, f"{alternativa}/cbc:PriceTypeCode") == "01"
    # valor unitario con 6 decimales: 4.20 / 1.18
    assert f.texto(xml, f"{LINEA}/cac:Price/cbc:PriceAmount") == "3.559322"


def test_el_valor_unitario_por_la_cantidad_cuadra_con_el_valor_de_venta() -> None:
    xml = f.arbol(f.factura_completa())
    for linea in xml.xpath("cac:InvoiceLine", namespaces=f.NS):
        precio = Decimal(linea.findtext("cac:Price/cbc:PriceAmount", namespaces=f.NS))
        cantidad = Decimal(linea.findtext("cbc:InvoicedQuantity", namespaces=f.NS))
        valor = Decimal(linea.findtext("cbc:LineExtensionAmount", namespaces=f.NS))
        assert abs(precio * cantidad - valor) <= Decimal("0.01")
