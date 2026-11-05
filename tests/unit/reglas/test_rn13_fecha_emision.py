"""RN-13 · Fecha y hora de emisión; la fecha no puede ser futura.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-13 · matriz filas 4 y 5.
"""

from __future__ import annotations

import datetime as dt

import pytest

from src.dominio.catalogos import TipoComprobante
from src.dominio.comprobante import Comprobante
from src.dominio.errores import ErrorReglaNegocio
from src.dominio.valores import Correlativo, Serie
from tests.unit.generacion_xml import fabrica as f


def test_el_xml_declara_fecha_y_hora_de_emision() -> None:
    xml = f.arbol(f.factura_contado())
    assert f.texto(xml, "cbc:IssueDate") == "2026-10-22"
    assert f.texto(xml, "cbc:IssueTime") == "10:30:00"


def test_una_fecha_futura_se_rechaza() -> None:
    with pytest.raises(ErrorReglaNegocio) as error:
        Comprobante(
            tipo=TipoComprobante.FACTURA,
            serie=Serie("F001"),
            correlativo=Correlativo(1),
            fecha_emision=dt.date(2999, 1, 1),
            hora_emision=dt.time(9, 0),
            emisor=f.EMISOR,
            cliente=f.CLIENTE_RUC,
            lineas=(f.linea(1),),
        )
    assert error.value.regla == "RN-13"
