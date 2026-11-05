"""Pruebas de la firma XMLDSig (J-12).

Trazabilidad: RN-18 (validar → **firmar** → enviar) · ADR-0002 (el certificado no sale del
servidor) · `src/puertos.py` (`IFirmaDigital`).

El certificado es de **prueba** y se genera en memoria: no se versiona ninguna clave.
"""

from __future__ import annotations

import datetime as dt

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from lxml import etree
from signxml import InvalidSignature, XMLVerifier

from src.adaptadores.salida.firma.xmldsig import DS_NS, EXT_NS, FirmadorXmlDsig
from src.adaptadores.salida.ubl.generador import GeneradorUblXsdata
from src.adaptadores.salida.ubl.validador import ValidadorXsd
from src.dominio.errores import ErrorDominio
from src.puertos import IFirmaDigital
from tests.unit.generacion_xml import escenarios as f


@pytest.fixture(scope="module")
def credenciales() -> tuple[bytes, bytes]:
    """Genera un par clave/certificado autofirmado de prueba (no se guarda en el repo)."""
    clave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nombre = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "ABC SOFTWARE CORP SAC - PRUEBA")])
    ahora = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nombre)
        .issuer_name(nombre)
        .public_key(clave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(ahora)
        .not_valid_after(ahora + dt.timedelta(days=3650))
        .sign(clave, hashes.SHA256())
    )
    clave_pem = clave.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    cert_pem = certificado.public_bytes(serialization.Encoding.PEM)
    return clave_pem, cert_pem


def _firmador(credenciales: tuple[bytes, bytes]) -> FirmadorXmlDsig:
    return FirmadorXmlDsig(*credenciales)


def test_el_firmador_implementa_el_puerto(credenciales) -> None:
    assert isinstance(_firmador(credenciales), IFirmaDigital)


def test_firmar_agrega_ext_ublextensions_y_la_firma(credenciales) -> None:
    xml = GeneradorUblXsdata().generar(f.factura_del_contrato())
    firmado = _firmador(credenciales).firmar(xml)
    arbol = etree.fromstring(firmado)
    assert arbol.find(f"{{{EXT_NS}}}UBLExtensions") is not None
    assert arbol.find(f".//{{{DS_NS}}}Signature") is not None


def test_la_firma_queda_dentro_de_extension_content(credenciales) -> None:
    xml = GeneradorUblXsdata().generar(f.factura_del_contrato())
    firmado = _firmador(credenciales).firmar(xml)
    ruta = (
        f"{{{EXT_NS}}}UBLExtensions/{{{EXT_NS}}}UBLExtension/"
        f"{{{EXT_NS}}}ExtensionContent/{{{DS_NS}}}Signature"
    )
    assert etree.fromstring(firmado).find(ruta) is not None


def test_el_xml_firmado_es_valido_para_signxml(credenciales) -> None:
    xml = GeneradorUblXsdata().generar(f.factura_del_contrato())
    firmado = _firmador(credenciales).firmar(xml)
    _, cert = credenciales
    resultado = XMLVerifier().verify(firmado, x509_cert=cert.decode("utf-8"))
    assert resultado.signed_xml is not None


def test_una_alteracion_posterior_rompe_la_firma(credenciales) -> None:
    xml = GeneradorUblXsdata().generar(f.factura_del_contrato())
    firmado = _firmador(credenciales).firmar(xml)
    alterado = firmado.replace(b"530.00", b"999.00")
    _, cert = credenciales
    with pytest.raises(InvalidSignature):
        XMLVerifier().verify(alterado, x509_cert=cert.decode("utf-8"))


def test_el_xml_firmado_sigue_siendo_valido_contra_el_esquema(credenciales) -> None:
    comprobante = f.factura_del_contrato()
    xml = GeneradorUblXsdata().generar(comprobante)
    firmado = _firmador(credenciales).firmar(xml)
    assert ValidadorXsd().validar(firmado, comprobante.tipo) == []


def test_no_se_firma_dos_veces(credenciales) -> None:
    xml = GeneradorUblXsdata().generar(f.factura_del_contrato())
    firmador = _firmador(credenciales)
    firmado = firmador.firmar(xml)
    with pytest.raises(ErrorDominio):
        firmador.firmar(firmado)
