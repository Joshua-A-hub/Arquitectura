"""RN-05 · IGV por línea (18 %) y su base (reglas SUNAT 3108 / 3277).

Trazabilidad: `specs/domain/reglas-negocio.md` RN-05 · matriz filas 35, 36 y 37
(`cac:TaxCategory/cbc:Percent`, `TaxableAmount`, `TaxAmount` del tributo 1000).
"""

from __future__ import annotations

from decimal import Decimal

from tests.unit.generacion_xml import fabrica as f

LINEA = "cac:InvoiceLine[{n}]"
TRIBUTO_IGV = "cac:TaxCategory/cac:TaxScheme/cbc:ID[text()='1000']"


def _subtotal_igv(xml, n: int):
    return xml.xpath(
        f"{LINEA.format(n=n)}/cac:TaxTotal/cac:TaxSubtotal[{TRIBUTO_IGV}]", namespaces=f.NS
    )[0]


def _texto(nodo, ruta: str) -> str:
    resultado = nodo.xpath(ruta, namespaces=f.NS)
    return resultado[0] if isinstance(resultado[0], str) else (resultado[0].text or "")


def test_el_igv_de_una_linea_gravada_es_18_por_ciento() -> None:
    xml = f.arbol(f.factura_contado())
    subtotal = _subtotal_igv(xml, 1)
    assert _texto(subtotal, "cac:TaxCategory/cbc:Percent") == "18.00"
    assert _texto(subtotal, "cac:TaxCategory/cbc:TaxExemptionReasonCode") == "10"
    assert _texto(subtotal, "cac:TaxCategory/cac:TaxScheme/cbc:ID") == "1000"
    assert _texto(subtotal, "cac:TaxCategory/cac:TaxScheme/cbc:Name") == "IGV"
    assert _texto(subtotal, "cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode") == "VAT"
    assert _texto(subtotal, "cbc:TaxAmount") == "32.03"


def test_la_base_del_igv_de_la_linea_incluye_el_isc() -> None:
    """Regla SUNAT 3108 (la base de la línea sí incluye el ISC)."""
    xml = f.arbol(f.factura_completa())  # cerveza: valor 81.36 + ISC 20.34 = 101.70
    subtotal = _subtotal_igv(xml, 3)
    assert _texto(subtotal, "cbc:TaxableAmount") == "101.70"
    assert _texto(subtotal, "cbc:TaxAmount") == "18.31"


def test_la_base_global_del_igv_no_incluye_el_isc() -> None:
    """Regla SUNAT 3277 (la base global es el valor de venta)."""
    comprobante = f.factura_completa()
    xml = f.arbol(comprobante)
    doc = xml.xpath(f"cac:TaxTotal/cac:TaxSubtotal[{TRIBUTO_IGV}]", namespaces=f.NS)[0]
    base = Decimal(_texto(doc, "cbc:TaxableAmount"))
    assert base == comprobante.totales.op_gravada
    assert base != comprobante.totales.valor_venta


def test_el_igv_de_cabecera_es_la_suma_del_igv_de_las_lineas() -> None:
    xml = f.arbol(f.factura_completa())
    doc = xml.xpath(f"cac:TaxTotal/cac:TaxSubtotal[{TRIBUTO_IGV}]", namespaces=f.NS)[0]
    total_doc = Decimal(_texto(doc, "cbc:TaxAmount"))
    # Líneas gravadas de la factura completa: 1 (arroz) y 5 (bolsa); las demás son
    # exonerada/inafecta o llevan ISC.
    lineas = (
        Decimal(_texto(_subtotal_igv(xml, 1), "cbc:TaxAmount"))
        + Decimal(_texto(_subtotal_igv(xml, 2), "cbc:TaxAmount"))
        + Decimal(_texto(_subtotal_igv(xml, 3), "cbc:TaxAmount"))
        + Decimal(_texto(_subtotal_igv(xml, 4), "cbc:TaxAmount"))
        + Decimal(_texto(_subtotal_igv(xml, 5), "cbc:TaxAmount"))
    )
    assert total_doc == lineas
