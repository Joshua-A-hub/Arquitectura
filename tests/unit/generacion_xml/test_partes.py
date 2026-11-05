"""Taller 2 · Generación: emisor y receptor (catálogo 06) y escape de caracteres."""

from __future__ import annotations

import pytest

from tests.unit.generacion_xml import fabrica as f

EMISOR = "cac:AccountingSupplierParty/cac:Party"
CLIENTE = "cac:AccountingCustomerParty/cac:Party"


def test_ruc_del_emisor_con_scheme_id_del_catalogo_06() -> None:
    xml = f.arbol(f.factura_contado())
    assert f.texto(xml, f"{EMISOR}/cac:PartyIdentification/cbc:ID") == "20123456786"
    assert f.texto(xml, f"{EMISOR}/cac:PartyIdentification/cbc:ID/@schemeID") == "6"
    assert f.texto(xml, f"{EMISOR}/cac:PartyIdentification/cbc:ID/@schemeURI").endswith("catalogo06")


def test_razon_social_ubigeo_y_direccion_del_emisor() -> None:
    xml = f.arbol(f.factura_contado())
    assert f.texto(xml, f"{EMISOR}/cac:PartyLegalEntity/cbc:RegistrationName") == "ABC SOFTWARE CORP SAC"
    assert f.texto(xml, f"{EMISOR}/cac:PartyLegalEntity/cac:RegistrationAddress/cbc:ID") == "150101"
    assert f.texto(xml, f"{EMISOR}/cac:PartyLegalEntity/cac:RegistrationAddress/cbc:StreetName") == "AV. COLONIAL 456"


def test_cliente_con_ruc_en_factura() -> None:
    xml = f.arbol(f.factura_contado())
    assert f.texto(xml, f"{CLIENTE}/cac:PartyIdentification/cbc:ID") == "20512345671"
    assert f.texto(xml, f"{CLIENTE}/cac:PartyIdentification/cbc:ID/@schemeID") == "6"
    assert f.texto(xml, f"{CLIENTE}/cac:PartyLegalEntity/cbc:RegistrationName").startswith("DISTRIBUIDORA")


def test_cliente_con_dni_en_boleta() -> None:
    xml = f.arbol(f.boleta())
    assert f.texto(xml, f"{CLIENTE}/cac:PartyIdentification/cbc:ID") == "45678912"
    assert f.texto(xml, f"{CLIENTE}/cac:PartyIdentification/cbc:ID/@schemeID") == "1"


def test_cliente_no_domiciliado_en_exportacion() -> None:
    xml = f.arbol(f.factura_exportacion_usd())
    assert f.texto(xml, f"{CLIENTE}/cac:PartyIdentification/cbc:ID/@schemeID") == "0"


def test_el_ampersand_de_la_razon_social_se_escapa() -> None:
    xml_bytes = f.generar(f.factura_contado())
    assert b"EL SOL & CIA" not in xml_bytes  # el & crudo rompería el XML
    xml = f.arbol(f.factura_contado())
    assert f.texto(xml, f"{CLIENTE}/cac:PartyLegalEntity/cbc:RegistrationName") == "DISTRIBUIDORA EL SOL & CIA S.A.C."


def test_el_cliente_sin_direccion_no_genera_direccion() -> None:
    xml = f.arbol(f.boleta())
    assert not xml.xpath(f"{CLIENTE}/cac:PartyLegalEntity/cac:RegistrationAddress", namespaces=f.NS)


def test_la_direccion_del_cliente_se_omite_si_esta_vacia() -> None:
    xml = f.arbol(f.factura_contado())
    assert (
        f.texto(xml, f"{CLIENTE}/cac:PartyLegalEntity/cac:RegistrationAddress/cbc:StreetName")
        == "JR. COMERCIO 123, LIMA"
    )


@pytest.mark.parametrize(
    ("escenario", "scheme"),
    [("factura-contado", "6"), ("boleta", "1"), ("factura-exportacion-usd", "0")],
)
def test_scheme_id_por_tipo_de_documento(escenario: str, scheme: str) -> None:
    xml = f.arbol(f.ESCENARIOS[escenario]())
    assert f.texto(xml, f"{CLIENTE}/cac:PartyIdentification/cbc:ID/@schemeID") == scheme


def test_codigo_de_establecimiento_del_emisor() -> None:
    xml = f.arbol(f.factura_contado())
    direccion = f"{EMISOR}/cac:PartyLegalEntity/cac:RegistrationAddress"
    assert f.texto(xml, f"{direccion}/cbc:AddressTypeCode") == "0000"
    assert f.texto(xml, f"{direccion}/cbc:AddressTypeCode/@listName") == "Establecimientos anexos"


def test_ubigeo_del_cliente_cuando_lo_tiene() -> None:
    from src.dominio.comprobante import Cliente as ClienteDominio
    from src.dominio.valores import DocumentoIdentidad

    cliente = ClienteDominio(
        DocumentoIdentidad(f.TipoDocumentoIdentidad.RUC, "20512345671"),
        "DISTRIBUIDORA SELVA SAC",
        direccion="AV. ARGENTINA 123",
        ubigeo="150101",
    )
    xml = f.arbol(f.armar(f.TipoComprobante.FACTURA, "F001", (f.linea(1),), cliente=cliente))
    assert f.texto(xml, f"{CLIENTE}/cac:PartyLegalEntity/cac:RegistrationAddress/cbc:ID") == "150101"


def test_boleta_a_consumidor_final() -> None:
    from src.dominio.comprobante import Cliente as ClienteDominio
    from src.dominio.valores import DocumentoIdentidad

    cliente = ClienteDominio(DocumentoIdentidad(f.TipoDocumentoIdentidad.NO_DOMICILIADO, "0"), "CLIENTES VARIOS")
    xml = f.arbol(f.armar(f.TipoComprobante.BOLETA, "B001", (f.linea(1),), cliente=cliente))
    assert f.texto(xml, f"{CLIENTE}/cac:PartyIdentification/cbc:ID") == "0"
    assert f.texto(xml, f"{CLIENTE}/cac:PartyIdentification/cbc:ID/@schemeID") == "0"
