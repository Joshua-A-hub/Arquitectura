"""Leyenda 1000: el importe en letras del comprobante.

Trazabilidad: matriz fila 6 (leyendas) · `specs/contracts/ubl/perfil-invoice.md` §3
(`cbc:Note[@languageLocaleID='1000']`).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from src.dominio.catalogos import Moneda
from src.dominio.letras import monto_en_letras
from tests.unit.generacion_xml import fabrica as f


@pytest.mark.parametrize(
    ("importe", "letras"),
    [
        ("0.00", "CERO CON 00/100 SOLES"),
        ("1.00", "UNO CON 00/100 SOLES"),
        ("21.00", "VEINTIUNO CON 00/100 SOLES"),
        ("100.00", "CIEN CON 00/100 SOLES"),
        ("530.00", "QUINIENTOS TREINTA CON 00/100 SOLES"),
        ("1000.00", "MIL CON 00/100 SOLES"),
        ("2500.50", "DOS MIL QUINIENTOS CON 50/100 SOLES"),
        ("1000000.00", "UN MILLÓN CON 00/100 SOLES"),
    ],
)
def test_importe_en_letras(importe: str, letras: str) -> None:
    assert monto_en_letras(Decimal(importe)) == letras


def test_el_xml_lleva_la_leyenda_1000_con_el_importe_en_letras() -> None:
    xml = f.arbol(f.factura_contado())
    assert f.texto(xml, "cbc:Note[@languageLocaleID='1000']") == (
        "DOSCIENTOS DIEZ CON 00/100 SOLES"
    )


def test_la_leyenda_usa_la_moneda_del_comprobante() -> None:
    xml = f.arbol(f.factura_exportacion_usd())
    assert f.texto(xml, "cbc:Note[@languageLocaleID='1000']").endswith("DÓLARES AMERICANOS")
    assert monto_en_letras(Decimal("1.00"), Moneda.USD).endswith("DÓLARES AMERICANOS")
