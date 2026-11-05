"""RN-09 · Totales del comprobante: calculados, nunca recibidos.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-09 · matriz filas 40 a 45
(`cac:TaxTotal/cbc:TaxAmount` y `cac:LegalMonetaryTotal`).
"""

from __future__ import annotations

from decimal import Decimal

from tests.unit.generacion_xml import escenarios as f


def test_total_monetario_de_la_factura() -> None:
    xml = f.arbol(f.factura_del_contrato())
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:LineExtensionAmount") == "449.83"
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount") == "530.00"
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:PayableAmount") == "530.00"


def test_payable_amount_coincide_con_el_total_con_impuestos() -> None:
    xml = f.arbol(f.factura_con_isc_de_tres_sistemas())
    con_impuestos = f.texto(xml, "cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount")
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:PayableAmount") == con_impuestos


def test_el_total_del_xml_coincide_con_el_del_dominio() -> None:
    comprobante = f.factura_con_isc_de_tres_sistemas()
    xml = f.arbol(comprobante)
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:PayableAmount") == (
        f"{comprobante.totales.importe_total:.2f}"
    )


def test_el_total_de_impuestos_suma_los_subtotales() -> None:
    xml = f.arbol(f.factura_con_isc_de_tres_sistemas())
    total = Decimal(f.texto(xml, "cac:TaxTotal/cbc:TaxAmount"))
    subtotales = f.todos(xml, "cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount")
    assert total == sum((Decimal(s) for s in subtotales), start=Decimal("0.00"))


def test_el_documento_declara_un_subtotal_por_tributo() -> None:
    xml = f.arbol(f.factura_con_isc_de_tres_sistemas())
    codigos = f.todos(xml, "cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID")
    assert codigos == ["1000", "2000", "9997", "9998", "7152"]


def test_los_totales_del_dominio_parten_de_las_operaciones() -> None:
    totales = f.factura_con_isc_de_tres_sistemas().totales
    suma_operaciones = (
        totales.op_gravada + totales.op_exonerada + totales.op_inafecta + totales.op_exportacion
    )
    assert totales.valor_venta == suma_operaciones
    assert totales.importe_total == totales.valor_venta + totales.total_impuestos
