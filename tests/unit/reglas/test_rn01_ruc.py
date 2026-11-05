"""RN-01 · RUC del emisor con dígito verificador (módulo 11).

Trazabilidad: `specs/domain/reglas-negocio.md` RN-01 · matriz fila 14
(`cac:AccountingSupplierParty/.../cbc:ID` con `@schemeID=6`).
"""

from __future__ import annotations

import pytest

from src.dominio.errores import ErrorReglaNegocio
from src.dominio.valores import RUC
from tests.unit.generacion_xml import fabrica as f


@pytest.mark.parametrize("ruc", ["20123456786", "20512345671", "10000000006"])
def test_ruc_con_digito_verificador_valido(ruc: str) -> None:
    assert RUC.es_valido(ruc)


@pytest.mark.parametrize("ruc", ["20123456780", "12345678901", "20A23456786", "2012345"])
def test_ruc_invalido(ruc: str) -> None:
    assert not RUC.es_valido(ruc)


def test_construir_un_ruc_invalido_lanza_regla_de_negocio() -> None:
    with pytest.raises(ErrorReglaNegocio) as error:
        RUC("20123456780")
    assert error.value.regla == "RN-01"


def test_el_ruc_del_emisor_llega_al_xml_con_scheme_id_del_catalogo_06() -> None:
    xml = f.arbol(f.factura_contado())
    emisor = "cac:AccountingSupplierParty/cac:Party"
    assert f.texto(xml, f"{emisor}/cac:PartyIdentification/cbc:ID") == "20123456786"
    assert f.texto(xml, f"{emisor}/cac:PartyIdentification/cbc:ID/@schemeID") == "6"
