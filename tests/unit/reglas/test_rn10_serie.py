"""RN-10 · Serie del comprobante: cuatro caracteres alfanuméricos y coherente con el tipo.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-10 · matriz fila 2
(`cbc:ID` = serie_numero).
"""

from __future__ import annotations

import pytest

from src.dominio.catalogos import TipoComprobante
from src.dominio.errores import ErrorReglaNegocio
from src.dominio.valores import Serie
from tests.unit.generacion_xml import escenarios as f


@pytest.mark.parametrize("serie", ["F001", "FC01", "BA01", "B9Z2"])
def test_series_alfanumericas_validas(serie: str) -> None:
    Serie(serie)


@pytest.mark.parametrize("serie", ["F01", "001", "F0001", "f001"])
def test_series_fuera_de_formato_se_rechazan(serie: str) -> None:
    with pytest.raises(ErrorReglaNegocio):
        Serie(serie)


def test_una_factura_no_puede_usar_serie_de_boleta() -> None:
    with pytest.raises(ErrorReglaNegocio):
        Serie("B001").validar_para(TipoComprobante.FACTURA)


def test_el_xml_lleva_serie_numero_en_cbc_id() -> None:
    xml = f.arbol(f.factura_del_contrato())
    assert f.texto(xml, "cbc:ID") == "F001-00000123"


def test_una_serie_alfanumerica_llega_al_xml() -> None:
    comprobante = f.armar(TipoComprobante.FACTURA, "FA01", (f.linea(1),))
    xml = f.arbol(comprobante)
    assert f.texto(xml, "cbc:ID") == "FA01-00000001"
