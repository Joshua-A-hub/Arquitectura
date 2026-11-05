"""RN-23 · El documento informal del legado no se convierte en comprobante.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-23 · matriz fila 58 ·
catálogo 12 (documento relacionado, tipo `99`).
"""

from __future__ import annotations

from tests.unit.generacion_xml import escenarios as f


def test_el_vale_del_legado_viaja_como_documento_relacionado() -> None:
    xml = f.arbol(f.factura_migrada_con_vale())
    assert f.texto(xml, "cac:AdditionalDocumentReference/cbc:ID") == "VALE-SALIDA-0042"
    assert f.texto(xml, "cac:AdditionalDocumentReference/cbc:DocumentTypeCode") == "99"


def test_una_factura_sin_documentos_del_legado_no_los_declara() -> None:
    xml = f.arbol(f.factura_del_contrato())
    assert not xml.xpath("cac:AdditionalDocumentReference", namespaces=f.NS)
