"""RN-07 · ICBPER: monto fijo por bolsa, con monto unitario y cantidad de bolsas.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-07 · matriz fila 39 (ICBPER).
Corrige lo señalado en J-5: el XML de ejemplo (y el generado) debe declarar
`cbc:BaseUnitMeasure` y `cbc:PerUnitAmount`, no solo el importe.
"""

from __future__ import annotations

from decimal import Decimal

from tests.unit.generacion_xml import escenarios as f

NS = f.NS


def _subtotal_icbper(nodo):
    return nodo.xpath(
        ".//cac:TaxSubtotal[cac:TaxCategory/cac:TaxScheme/cbc:ID='7152']", namespaces=NS
    )[0]


def _texto(nodo, ruta: str) -> str:
    resultado = nodo.xpath(ruta, namespaces=NS)
    return resultado[0] if isinstance(resultado[0], str) else (resultado[0].text or "")


def test_la_linea_de_bolsa_declara_monto_unitario_y_cantidad() -> None:
    xml = f.arbol(f.factura_con_isc_de_tres_sistemas())  # línea 5: 3 bolsas
    linea = xml.xpath("cac:InvoiceLine[4]", namespaces=NS)[0]
    subtotal = _subtotal_icbper(linea)
    assert _texto(subtotal, "cac:TaxCategory/cbc:PerUnitAmount") == "0.50"
    assert Decimal(_texto(subtotal, "cbc:BaseUnitMeasure")) == Decimal("3")
    assert _texto(subtotal, "cbc:TaxAmount") == "1.50"


def test_el_documento_declara_el_icbper_con_su_unidad() -> None:
    xml = f.arbol(f.factura_con_isc_de_tres_sistemas())
    subtotal = _subtotal_icbper(xml)
    assert _texto(subtotal, "cac:TaxCategory/cbc:PerUnitAmount") == "0.50"
    assert Decimal(_texto(subtotal, "cbc:BaseUnitMeasure")) == Decimal("3")
    assert _texto(subtotal, "cbc:TaxAmount") == "1.50"


def test_el_importe_es_cincuenta_centimos_por_bolsa() -> None:
    comprobante = f.factura_con_isc_de_tres_sistemas()
    bolsas = sum(linea.cantidad for linea in comprobante.lineas if linea.aplica_icbper)
    assert comprobante.totales.total_icbper == Decimal("0.50") * bolsas
