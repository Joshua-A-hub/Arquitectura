"""RN-18 · El XML generado es conforme al esquema oficial de OASIS.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-18 (validar antes de firmar) ·
matriz fila 51 (firma) · `specs/adr/0002-ubl-sunat-y-validacion-xsd.md`.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from lxml import etree

from tests.unit.generacion_xml import fabrica as f

RAIZ = Path(__file__).resolve().parents[3]
XSD = {
    "Invoice": RAIZ / "specs/contracts/ubl/oficial/maindoc/UBL-Invoice-2.1.xsd",
    "CreditNote": RAIZ / "specs/contracts/ubl/oficial/maindoc/UBL-CreditNote-2.1.xsd",
    "DebitNote": RAIZ / "specs/contracts/ubl/oficial/maindoc/UBL-DebitNote-2.1.xsd",
}


@pytest.mark.parametrize("escenario", sorted(f.ESCENARIOS))
def test_el_xml_generado_valida_contra_el_esquema_oficial(escenario: str) -> None:
    xml = f.generar(f.ESCENARIOS[escenario]())
    raiz = etree.QName(etree.fromstring(xml)).localname
    esquema = etree.XMLSchema(etree.parse(str(XSD[raiz])))
    assert esquema.validate(etree.fromstring(xml)), "\n".join(
        f"línea {e.line}: {e.message}" for e in list(esquema.error_log)[:5]
    )


def test_caracteres_especiales_producen_xml_valido() -> None:
    linea = f.linea(1, 'CAFÉ & TÉ <especial> "Ñ" € ]]> fin')
    comprobante = f.armar(f.TipoComprobante.FACTURA, "F001", (linea,))
    xml = f.generar(comprobante)
    esquema = etree.XMLSchema(etree.parse(str(XSD["Invoice"])))
    assert esquema.validate(etree.fromstring(xml))
    arbol = etree.fromstring(xml)
    assert f.texto(arbol, "cac:InvoiceLine/cac:Item/cbc:Description") == (
        'CAFÉ & TÉ <especial> "Ñ" € ]]> fin'
    )


def test_el_ampersand_se_escapa_en_el_xml() -> None:
    xml_bytes = f.generar(f.factura_contado())
    assert b"EL SOL & CIA" not in xml_bytes
    xml = f.arbol(f.factura_contado())
    cliente = "cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity"
    assert f.texto(xml, f"{cliente}/cbc:RegistrationName") == "DISTRIBUIDORA EL SOL & CIA S.A.C."
