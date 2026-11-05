"""Regresión contra el XML de referencia («golden files»).

Los XML de `esperados/` guardan la forma exacta de cada escenario: si un cambio altera
el documento, la prueba falla y obliga a revisar la diferencia. **No** demuestran que el
XML sea correcto (de eso se encargan las pruebas de reglas y la conformidad XSD), solo
que no cambió sin querer.

Para regenerarlos cuando el cambio es intencional:

    $env:ACTUALIZAR_ESPERADOS="1"; pytest tests/unit/generacion_xml; Remove-Item Env:ACTUALIZAR_ESPERADOS
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests.unit.generacion_xml import fabrica as f

ESPERADOS = Path(__file__).parent / "esperados"


@pytest.mark.parametrize("escenario", sorted(f.ESCENARIOS))
def test_regresion_contra_el_xml_de_referencia(escenario: str) -> None:
    ESPERADOS.mkdir(exist_ok=True)
    archivo = ESPERADOS / f"{escenario}.xml"
    xml = f.generar(f.ESCENARIOS[escenario]())
    if os.environ.get("ACTUALIZAR_ESPERADOS") == "1":
        archivo.write_bytes(xml)
    assert archivo.exists(), f"falta el XML de referencia {archivo.name}"
    assert xml == archivo.read_bytes(), (
        f"el XML de {escenario} cambió respecto a {archivo.name}; "
        "si el cambio es intencional, regenera con ACTUALIZAR_ESPERADOS=1"
    )


def test_dos_instancias_del_generador_producen_el_mismo_xml() -> None:
    from src.adaptadores.salida.ubl.generador import GeneradorUblXsdata

    comprobante = f.factura_completa()
    assert GeneradorUblXsdata().generar(comprobante) == GeneradorUblXsdata().generar(comprobante)
