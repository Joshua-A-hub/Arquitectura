"""RN-25 · Forma de pago obligatoria en factura y boleta (RS 193-2020).

Trazabilidad: `specs/domain/reglas-negocio.md` RN-25 · matriz fila de forma de pago.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal as D

from src.dominio.catalogos import TipoComprobante, TipoFormaPago
from src.dominio.comprobante import Cuota, FormaPago
from tests.unit.generacion_xml import escenarios as f


def _medios(xml) -> list[str]:
    return f.todos(xml, "cac:PaymentTerms/cbc:PaymentMeansID")


def test_una_factura_sin_forma_de_pago_asume_contado() -> None:
    comprobante = f.armar(TipoComprobante.FACTURA, "F001", (f.linea(1),))
    assert comprobante.forma_pago is not None
    assert comprobante.forma_pago.tipo is TipoFormaPago.CONTADO
    assert _medios(f.arbol(comprobante)) == ["Contado"]


def test_una_boleta_sin_forma_de_pago_asume_contado() -> None:
    comprobante = f.armar(TipoComprobante.BOLETA, "B001", (f.linea(1),), cliente=f.CLIENTE_DNI)
    assert _medios(f.arbol(comprobante)) == ["Contado"]


def test_la_forma_de_pago_al_credito_respeta_las_cuotas() -> None:
    cuotas = (Cuota(D("225.00"), dt.date(2026, 11, 21)), Cuota(D("225.00"), dt.date(2026, 12, 21)))
    comprobante = f.armar(
        TipoComprobante.FACTURA,
        "F001",
        (f.linea(1),),
        forma_pago=FormaPago(TipoFormaPago.CREDITO, cuotas),
    )
    assert _medios(f.arbol(comprobante)) == ["Credito", "Cuota001", "Cuota002"]


def test_la_nota_no_exige_forma_de_pago() -> None:
    nota = f.nota_credito_por_devolucion()
    assert nota.forma_pago is None
    assert _medios(f.arbol(nota)) == []


def test_la_forma_de_pago_declarada_no_se_pisa() -> None:
    contado = FormaPago(TipoFormaPago.CONTADO)
    comprobante = f.armar(TipoComprobante.FACTURA, "F001", (f.linea(1),), forma_pago=contado)
    assert comprobante.forma_pago is contado
