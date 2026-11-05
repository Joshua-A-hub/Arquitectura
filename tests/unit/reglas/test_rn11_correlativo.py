"""RN-11 · Correlativo: entero positivo, incremental y con formato de 8 dígitos.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-11 · matriz fila 2
(`cbc:ID` = `serie_numero`).
"""

from __future__ import annotations

import pytest

from src.dominio.errores import ErrorReglaNegocio
from src.dominio.valores import Correlativo
from tests.unit.generacion_xml import escenarios as f


def test_el_correlativo_se_formatea_a_ocho_digitos() -> None:
    assert str(Correlativo(123)) == "00000123"


@pytest.mark.parametrize("valor", [0, -1, 100_000_000])
def test_correlativo_fuera_de_rango(valor: int) -> None:
    with pytest.raises(ErrorReglaNegocio):
        Correlativo(valor)


def test_el_xml_refleja_el_correlativo() -> None:
    comprobante = f.armar(f.TipoComprobante.FACTURA, "F001", (f.linea(1),), correlativo=12_345_678)
    xml = f.arbol(comprobante)
    assert f.texto(xml, "cbc:ID") == "F001-12345678"


def test_el_ejemplo_del_contrato_usa_su_correlativo() -> None:
    assert f.factura_del_contrato().serie_numero == "F001-00000123"
