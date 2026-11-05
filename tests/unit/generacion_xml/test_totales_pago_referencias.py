"""Taller 2 · Generación: totales, forma de pago y referencias de notas."""

from __future__ import annotations

import pytest

from src.dominio.catalogos import MotivoNotaCredito, MotivoNotaDebito
from tests.unit.generacion_xml import fabrica as f

# --- totales del comprobante -------------------------------------------------------


def test_total_monetario_de_la_factura() -> None:
    xml = f.arbol(f.factura_contado())
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:LineExtensionAmount") == "177.97"
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount") == "210.00"
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:PayableAmount") == "210.00"


def test_payable_amount_coincide_con_el_total_con_impuestos() -> None:
    xml = f.arbol(f.factura_completa())
    con_impuestos = f.texto(xml, "cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount")
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:PayableAmount") == con_impuestos


def test_el_total_del_xml_coincide_con_el_del_dominio() -> None:
    comprobante = f.factura_completa()
    xml = f.arbol(comprobante)
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:PayableAmount") == f"{comprobante.importe_total:.2f}"


# --- forma de pago (RS 193-2020) ----------------------------------------------------


def test_forma_de_pago_al_contado() -> None:
    xml = f.arbol(
        f.armar(
            f.TipoComprobante.FACTURA,
            "F001",
            (f.linea(1),),
            forma_pago=f.FormaPago(f.TipoFormaPago.CONTADO),
        )
    )
    assert f.todos(xml, "cac:PaymentTerms/cbc:PaymentMeansID") == ["Contado"]


def test_forma_de_pago_al_credito_con_cuotas() -> None:
    import datetime as dt
    from decimal import Decimal as D

    from src.dominio.comprobante import Cuota

    cuotas = (Cuota(D("105.00"), dt.date(2026, 11, 21)), Cuota(D("105.00"), dt.date(2026, 12, 21)))
    xml = f.arbol(
        f.armar(
            f.TipoComprobante.FACTURA,
            "F001",
            (f.linea(1),),
            forma_pago=f.FormaPago(f.TipoFormaPago.CREDITO, cuotas),
        )
    )
    assert f.todos(xml, "cac:PaymentTerms/cbc:PaymentMeansID") == ["Credito", "Cuota001", "Cuota002"]
    assert f.todos(xml, "cac:PaymentTerms/cbc:PaymentDueDate") == ["2026-11-21", "2026-12-21"]
    assert f.texto(xml, "cac:PaymentTerms[1]/cbc:Amount") == "210.00"


def test_sin_forma_de_pago_no_se_emite_payment_terms() -> None:
    xml = f.arbol(f.factura_contado())
    assert not xml.xpath("cac:PaymentTerms", namespaces=f.NS)


@pytest.mark.parametrize(
    ("escenario", "cantidad_cuotas"),
    [("factura-credito", 2)],
)
def test_numero_de_cuotas(escenario: str, cantidad_cuotas: int) -> None:
    xml = f.arbol(f.ESCENARIOS[escenario]())
    medios = f.todos(xml, "cac:PaymentTerms/cbc:PaymentMeansID")
    assert len([m for m in medios if m.startswith("Cuota")]) == cantidad_cuotas


# --- notas de crédito y débito ------------------------------------------------------


def test_nota_de_credito_lleva_discrepancia_y_referencia() -> None:
    xml = f.arbol(f.nota_credito())
    assert f.texto(xml, "cac:DiscrepancyResponse/cbc:ReferenceID") == "F001-00000001"
    assert f.texto(xml, "cac:DiscrepancyResponse/cbc:ResponseCode") == MotivoNotaCredito.DEVOLUCION_ITEM.value
    assert f.texto(xml, "cac:DiscrepancyResponse/cbc:ResponseCode/@listURI").endswith("catalogo09")
    assert f.texto(xml, "cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID") == "F001-00000001"
    assert f.texto(xml, "cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode") == "01"


def test_nota_de_debito_usa_el_catalogo_10_y_requested_monetary_total() -> None:
    xml = f.arbol(f.nota_debito())
    assert f.texto(xml, "cac:DiscrepancyResponse/cbc:ResponseCode") == MotivoNotaDebito.INTERESES_MORA.value
    assert f.texto(xml, "cac:DiscrepancyResponse/cbc:ResponseCode/@listURI").endswith("catalogo10")
    assert xml.xpath("cac:RequestedMonetaryTotal", namespaces=f.NS)
    assert not xml.xpath("cac:LegalMonetaryTotal", namespaces=f.NS)


def test_el_sustento_de_la_nota_se_declara() -> None:
    xml = f.arbol(f.nota_credito())
    assert f.texto(xml, "cac:DiscrepancyResponse/cbc:Description") == "Sustento de la nota"


def test_la_nota_de_credito_tambien_cuadra_sus_totales() -> None:
    comprobante = f.nota_credito()
    xml = f.arbol(comprobante)
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:LineExtensionAmount") == "35.59"
    assert f.texto(xml, "cac:LegalMonetaryTotal/cbc:PayableAmount") == f"{comprobante.importe_total:.2f}"


# --- documentos del legado ----------------------------------------------------------


def test_el_vale_del_legado_viaja_como_documento_relacionado() -> None:
    xml = f.arbol(f.factura_de_vale())
    assert f.texto(xml, "cac:AdditionalDocumentReference/cbc:ID") == "VALE-SALIDA-0042"
    assert f.texto(xml, "cac:AdditionalDocumentReference/cbc:DocumentTypeCode") == "99"
