"""Los adaptadores cumplen los puertos declarados (arquitectura hexagonal).

Trazabilidad: `src/puertos.py` · ADR-0004 (implementación de `IXmlBuilder`) ·
`specs/architecture/mvc-hexagonal.md` (regla de dependencia).
"""

from __future__ import annotations

from src.adaptadores.salida.ubl.generador import GeneradorUblXsdata
from src.adaptadores.salida.ubl.validador import ValidadorXsd
from src.puertos import IValidadorXsd, IXmlBuilder
from tests.unit.generacion_xml import escenarios as f


def test_el_generador_implementa_el_puerto_ixmlbuilder() -> None:
    assert isinstance(GeneradorUblXsdata(), IXmlBuilder)


def test_el_validador_implementa_el_puerto_ivalidadorxsd() -> None:
    assert isinstance(ValidadorXsd(), IValidadorXsd)


def test_el_puerto_recibe_el_agregado_y_devuelve_xml() -> None:
    comprobante = f.factura_del_contrato()
    xml = GeneradorUblXsdata().construir(comprobante)
    assert xml.startswith(b"<?xml")
    assert b"F001-00000123" in xml


def test_el_validador_confirma_un_xml_generado() -> None:
    comprobante = f.factura_del_contrato()
    xml = GeneradorUblXsdata().construir(comprobante)
    assert ValidadorXsd().validar(xml, comprobante.tipo) == []


def test_el_validador_detecta_un_xml_alterado() -> None:
    comprobante = f.factura_del_contrato()
    xml = GeneradorUblXsdata().construir(comprobante).replace(
        b"<cbc:IssueDate>2026-10-22</cbc:IssueDate>",
        b"<cbc:IssueDate>22/10/2026</cbc:IssueDate>",
    )
    assert ValidadorXsd().validar(xml, comprobante.tipo)
