"""RN-08 · Redondeo tributario: base exacta y resultados a 2 decimales.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-08 · afecta a todos los importes del XML.
"""

from __future__ import annotations

import re
from decimal import Decimal

from src.dominio.catalogos import AfectacionIGV
from src.dominio.tributos import calcular_linea, redondear
from tests.unit.generacion_xml import escenarios as f


def test_redondeo_half_up() -> None:
    assert redondear("1.005") == Decimal("1.01")
    assert redondear("1.004") == Decimal("1.00")


def test_el_igv_se_calcula_sobre_la_base_exacta() -> None:
    """Redondear la base antes de multiplicar desviaba el IGV un céntimo (1.52 vs 1.53)."""
    calculado = calcular_linea(
        cantidad=Decimal("20"),
        precio_unitario=Decimal("0.50"),
        afectacion=AfectacionIGV.GRAVADO_ONEROSA,
    )
    assert calculado.valor_venta == Decimal("8.47")
    assert calculado.igv == Decimal("1.53")


def test_todos_los_importes_del_xml_llevan_dos_decimales() -> None:
    xml = f.arbol(f.factura_con_isc_de_tres_sistemas())
    importes = f.todos(xml, "//cbc:TaxAmount") + f.todos(xml, "//cbc:TaxableAmount")
    assert importes
    for importe in importes:
        assert re.fullmatch(r"-?\d+\.\d{2}", importe), f"importe sin 2 decimales: {importe}"


def test_los_totales_incluyen_todos_los_impuestos() -> None:
    xml = f.arbol(f.factura_con_isc_de_tres_sistemas())
    con_impuestos = Decimal(f.texto(xml, "cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount"))
    valor = Decimal(f.texto(xml, "cac:LegalMonetaryTotal/cbc:LineExtensionAmount"))
    impuestos = Decimal(f.texto(xml, "cac:TaxTotal/cbc:TaxAmount"))
    assert con_impuestos == valor + impuestos
