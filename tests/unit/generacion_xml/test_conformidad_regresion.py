"""Taller 2 · Generación: conformidad con el XSD oficial, determinismo y regresión.

Los XML de referencia («golden files») viven en `esperados/`. Si un cambio altera el XML,
la regresión falla y obliga a revisar la diferencia. Para regenerarlos:

    $env:ACTUALIZAR_ESPERADOS="1"; pytest tests/unit/generacion_xml; Remove-Item Env:ACTUALIZAR_ESPERADOS
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from lxml import etree

from tests.unit.generacion_xml import fabrica as f

RAIZ = Path(__file__).resolve().parents[3]
XSD_INVOICE = RAIZ / "specs" / "contracts" / "ubl" / "oficial" / "maindoc" / "UBL-Invoice-2.1.xsd"
XSD_CREDIT = RAIZ / "specs" / "contracts" / "ubl" / "oficial" / "maindoc" / "UBL-CreditNote-2.1.xsd"
XSD_DEBIT = RAIZ / "specs" / "contracts" / "ubl" / "oficial" / "maindoc" / "UBL-DebitNote-2.1.xsd"
ESPERADOS = Path(__file__).parent / "esperados"

ESQUEMAS = {
    "Invoice": XSD_INVOICE,
    "CreditNote": XSD_CREDIT,
    "DebitNote": XSD_DEBIT,
}


@pytest.mark.parametrize("escenario", sorted(f.ESCENARIOS))
def test_el_xml_generado_valida_contra_el_esquema_oficial(escenario: str) -> None:
    xml = f.generar(f.ESCENARIOS[escenario]())
    raiz = etree.QName(etree.fromstring(xml)).localname
    esquema = etree.XMLSchema(etree.parse(str(ESQUEMAS[raiz])))
    valido = esquema.validate(etree.fromstring(xml))
    assert valido, "\n".join(f"línea {e.line}: {e.message}" for e in list(esquema.error_log)[:5])


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


def test_la_generacion_es_determinista() -> None:
    primero = f.generar(f.factura_completa())
    segundo = f.generar(f.factura_completa())
    assert primero == segundo


def test_dos_instancias_del_generador_producen_el_mismo_xml() -> None:
    from src.adaptadores.salida.ubl.generador import GeneradorUblXsdata

    comprobante = f.factura_completa()
    assert GeneradorUblXsdata().generar(comprobante) == GeneradorUblXsdata().generar(comprobante)


def test_caracteres_especiales_producen_xml_valido() -> None:
    linea = f.linea(1, 'CAFÉ & TÉ <especial> "Ñ" € ]]> fin')
    comprobante = f.armar(f.TipoComprobante.FACTURA, "F001", (linea,))
    xml = f.generar(comprobante)
    esquema = etree.XMLSchema(etree.parse(str(XSD_INVOICE)))
    assert esquema.validate(etree.fromstring(xml))
    arbol = etree.fromstring(xml)
    assert f.texto(arbol, "cac:InvoiceLine/cac:Item/cbc:Description") == 'CAFÉ & TÉ <especial> "Ñ" € ]]> fin'


def test_el_xml_declara_utf8() -> None:
    assert b'encoding="UTF-8"' in f.generar(f.factura_contado())[:60]


def test_el_xml_no_lleva_bloque_de_firma() -> None:
    assert b"ext:UBLExtensions" not in f.generar(f.factura_completa())
