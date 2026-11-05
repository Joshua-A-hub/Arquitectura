"""Adaptador de firma: XMLDSig enveloped sobre el UBL, dentro de `ext:UBLExtensions`.

Implementa el puerto `IFirmaDigital` de `src/puertos.py` (RN-18: se firma **después** de validar
contra el esquema oficial). El certificado se configura al construir el adaptador y **nunca viaja al
cliente**: es un secreto de la empresa (ADR-0002).

Estructura que produce:

    <Invoice>
      <ext:UBLExtensions>
        <ext:UBLExtension>
          <ext:ExtensionContent>
            <ds:Signature>…</ds:Signature>
          </ext:ExtensionContent>
        </ext:UBLExtension>
      </ext:UBLExtensions>
      …
    </Invoice>
"""

from __future__ import annotations

from pathlib import Path

from lxml import etree
from signxml import XMLSigner, methods

from src.dominio.errores import ErrorDominio

EXT_NS = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
DS_NS = "http://www.w3.org/2000/09/xmldsig#"
C14N = "http://www.w3.org/2001/10/xml-exc-c14n#"


class FirmadorXmlDsig:
    """Implementa el puerto `IFirmaDigital`."""

    def __init__(self, clave: str | bytes | Path, certificado: str | bytes | Path) -> None:
        self._clave = _leer(clave)
        self._certificado = _leer(certificado).decode("utf-8")

    def firmar(self, xml: bytes) -> bytes:
        """Devuelve el XML firmado con `cac:Signature` dentro de `ext:UBLExtensions`."""
        raiz = etree.fromstring(xml)
        if raiz.find(f"{{{EXT_NS}}}UBLExtensions") is not None:
            raise ErrorDominio("el comprobante ya tiene un bloque de extensiones (¿ya está firmado?)")

        # El esqueleto de extensiones debe existir ANTES de firmar: la firma cubre el
        # documento sin el nodo ds:Signature, y el hueco donde se inserta.
        extensiones = etree.Element(f"{{{EXT_NS}}}UBLExtensions", nsmap={"ext": EXT_NS})
        extension = etree.SubElement(extensiones, f"{{{EXT_NS}}}UBLExtension")
        etree.SubElement(extension, f"{{{EXT_NS}}}ExtensionContent")
        raiz.insert(0, extensiones)

        firmante = XMLSigner(
            method=methods.enveloped,
            signature_algorithm="rsa-sha256",
            digest_algorithm="sha256",
            c14n_algorithm=C14N,
        )
        firmado = firmante.sign(raiz, key=self._clave, cert=self._certificado)

        # Mover la firma al hueco de ExtensionContent (estructura que exige SUNAT).
        firma = firmado.find(f".//{{{DS_NS}}}Signature")
        contenido = firmado.find(
            f"{{{EXT_NS}}}UBLExtensions/{{{EXT_NS}}}UBLExtension/{{{EXT_NS}}}ExtensionContent"
        )
        if firma is None or contenido is None:
            raise ErrorDominio("signxml no produjo la firma esperada")
        firma.getparent().remove(firma)
        contenido.append(firma)

        return etree.tostring(firmado, xml_declaration=True, encoding="UTF-8")


def _leer(origen: str | bytes | Path) -> bytes:
    if isinstance(origen, bytes):
        return origen
    if isinstance(origen, str):
        return origen.encode("utf-8")
    return Path(origen).read_bytes()
