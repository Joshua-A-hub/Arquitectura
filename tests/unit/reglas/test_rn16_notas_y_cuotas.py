"""RN-16 · Notas de crédito/débito y cuotas de la venta al crédito.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-16 · matriz filas 46 a 50
(`cac:BillingReference`, `cac:DiscrepancyResponse`, `cac:PaymentTerms`).
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal as D

import pytest

from src.dominio.catalogos import MotivoNotaCredito, MotivoNotaDebito, TipoComprobante, TipoFormaPago
from src.dominio.comprobante import Cuota, FormaPago
from src.dominio.errores import ErrorReglaNegocio
from tests.unit.generacion_xml import fabrica as f


def test_nota_de_credito_lleva_discrepancia_y_referencia() -> None:
    xml = f.arbol(f.nota_credito())
    assert f.texto(xml, "cac:DiscrepancyResponse/cbc:ReferenceID") == "F001-00000001"
    assert f.texto(xml, "cac:DiscrepancyResponse/cbc:ResponseCode") == (
        MotivoNotaCredito.DEVOLUCION_ITEM.value
    )
    assert f.texto(xml, "cac:DiscrepancyResponse/cbc:ResponseCode/@listURI").endswith("catalogo09")
    assert f.texto(xml, "cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID") == "F001-00000001"
    assert f.texto(xml, "cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode") == "01"


def test_nota_de_debito_usa_catalogo_10_y_requested_monetary_total() -> None:
    xml = f.arbol(f.nota_debito())
    assert f.texto(xml, "cac:DiscrepancyResponse/cbc:ResponseCode") == (
        MotivoNotaDebito.INTERESES_MORA.value
    )
    assert f.texto(xml, "cac:DiscrepancyResponse/cbc:ResponseCode/@listURI").endswith("catalogo10")
    assert xml.xpath("cac:RequestedMonetaryTotal", namespaces=f.NS)
    assert not xml.xpath("cac:LegalMonetaryTotal", namespaces=f.NS)


def test_el_sustento_de_la_nota_se_declara() -> None:
    xml = f.arbol(f.nota_credito())
    assert f.texto(xml, "cac:DiscrepancyResponse/cbc:Description") == "Sustento de la nota"


def test_la_nota_de_credito_cuadra_sus_totales() -> None:
    comprobante = f.nota_credito()
    xml = f.arbol(comprobante)
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:LineExtensionAmount") == "35.59"
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:PayableAmount") == (
        f"{comprobante.totales.importe_total:.2f}"
    )


def test_una_nota_sin_referencia_se_rechaza() -> None:
    with pytest.raises(ErrorReglaNegocio):
        f.armar(
            TipoComprobante.NOTA_CREDITO,
            "FC01",
            (f.linea(1),),
            motivo=MotivoNotaCredito.DEVOLUCION_ITEM,
        )


def test_una_nota_no_puede_referenciar_otra_nota() -> None:
    with pytest.raises(ErrorReglaNegocio):
        f.armar(
            TipoComprobante.NOTA_CREDITO,
            "FC01",
            (f.linea(1),),
            referencia=f.nota_credito(),
            motivo=MotivoNotaCredito.DEVOLUCION_ITEM,
        )


def test_el_credito_exige_cuotas() -> None:
    with pytest.raises(ErrorReglaNegocio):
        FormaPago(TipoFormaPago.CREDITO)


def test_el_contado_no_admite_cuotas() -> None:
    with pytest.raises(ErrorReglaNegocio):
        FormaPago(TipoFormaPago.CONTADO, (Cuota(D("10.00"), dt.date(2026, 11, 21)),))


def test_las_cuotas_deben_sumar_el_importe_total() -> None:
    cuotas = (
        Cuota(D("100.00"), dt.date(2026, 11, 21)),
        Cuota(D("50.00"), dt.date(2026, 12, 21)),
    )
    with pytest.raises(ErrorReglaNegocio):
        f.armar(
            TipoComprobante.FACTURA,
            "F001",
            (f.linea(1),),  # total 210.00
            forma_pago=FormaPago(TipoFormaPago.CREDITO, cuotas),
        )


def test_cuotas_que_suman_el_total_se_aceptan() -> None:
    cuotas = (
        Cuota(D("105.00"), dt.date(2026, 11, 21)),
        Cuota(D("105.00"), dt.date(2026, 12, 21)),
    )
    assert f.armar(
        TipoComprobante.FACTURA,
        "F001",
        (f.linea(1),),
        forma_pago=FormaPago(TipoFormaPago.CREDITO, cuotas),
    )


def test_la_nota_de_credito_usa_cantidad_acreditada() -> None:
    xml = f.arbol(f.nota_credito())
    assert xml.xpath("cac:CreditNoteLine", namespaces=f.NS)
    assert f.texto(xml, "cac:CreditNoteLine/cbc:CreditedQuantity") == "10"


def test_la_nota_de_debito_usa_cantidad_debitada() -> None:
    xml = f.arbol(f.nota_debito())
    assert xml.xpath("cac:DebitNoteLine", namespaces=f.NS)
    assert f.texto(xml, "cac:DebitNoteLine/cbc:DebitedQuantity") == "1"
