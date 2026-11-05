"""RN-03 · Integridad del receptor y datos del emisor.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-03 · matriz filas 21 y 22
(razón social, dirección y ubigeo de las partes).
"""

from __future__ import annotations

import pytest

from src.dominio.comprobante import Cliente as ClienteDominio
from src.dominio.comprobante import Emisor
from src.dominio.errores import ErrorReglaNegocio
from src.dominio.valores import RUC, DocumentoIdentidad
from tests.unit.generacion_xml import escenarios as f

EMISOR = "cac:AccountingSupplierParty/cac:Party"
CLIENTE = "cac:AccountingCustomerParty/cac:Party"


def test_la_razon_social_del_cliente_es_obligatoria() -> None:
    with pytest.raises(ErrorReglaNegocio):
        ClienteDominio(DocumentoIdentidad(f.TipoDocumentoIdentidad.RUC, "20512345671"), "AB")


def test_el_ubigeo_del_emisor_debe_tener_seis_digitos() -> None:
    with pytest.raises(ErrorReglaNegocio):
        Emisor(ruc=RUC("20123456786"), razon_social="ABC SOFTWARE CORP SAC", ubigeo="15")


def test_el_xml_lleva_razon_social_ubigeo_y_direccion_del_emisor() -> None:
    xml = f.arbol(f.factura_del_contrato())
    legal = f"{EMISOR}/cac:PartyLegalEntity"
    assert f.texto(xml, f"{legal}/cbc:RegistrationName") == "ABC SOFTWARE CORP SAC"
    assert f.texto(xml, f"{legal}/cac:RegistrationAddress/cbc:ID") == "150101"
    assert f.texto(xml, f"{legal}/cac:RegistrationAddress/cbc:StreetName") == "AV. COLONIAL 456"


def test_el_codigo_de_establecimiento_del_emisor_se_declara() -> None:
    xml = f.arbol(f.factura_del_contrato())
    direccion = f"{EMISOR}/cac:PartyLegalEntity/cac:RegistrationAddress"
    assert f.texto(xml, f"{direccion}/cbc:AddressTypeCode") == "0000"
    assert f.texto(xml, f"{direccion}/cbc:AddressTypeCode/@listName") == "Establecimientos anexos"


def test_el_ubigeo_del_cliente_se_declara_cuando_existe() -> None:
    cliente = ClienteDominio(
        DocumentoIdentidad(f.TipoDocumentoIdentidad.RUC, "20512345671"),
        "DISTRIBUIDORA SELVA SAC",
        direccion="AV. ARGENTINA 123",
        ubigeo="150101",
    )
    xml = f.arbol(f.armar(f.TipoComprobante.FACTURA, "F001", (f.linea(1),), cliente=cliente))
    direccion = f"{CLIENTE}/cac:PartyLegalEntity/cac:RegistrationAddress"
    assert f.texto(xml, f"{direccion}/cbc:ID") == "150101"


def test_el_cliente_sin_direccion_no_genera_bloque_de_direccion() -> None:
    xml = f.arbol(f.boleta_con_dni())
    assert not xml.xpath(
        f"{CLIENTE}/cac:PartyLegalEntity/cac:RegistrationAddress", namespaces=f.NS
    )
