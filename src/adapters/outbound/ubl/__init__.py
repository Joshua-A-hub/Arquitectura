"""Adaptador de salida UBL 2.1: constantes de namespaces y catálogos.

Las clases de `generated/` las produce `xsdata` desde los XSD oficiales de OASIS
(`specs/contracts/ubl/oficial/`). Este paquete contiene el código que **sí** se escribe a mano:
el adaptador que traduce el dominio a esas clases y el validador contra el esquema.
"""

from __future__ import annotations

NAMESPACES: dict[str, str] = {
    "Invoice": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "CreditNote": "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2",
    "DebitNote": "urn:oasis:names:specification:ubl:schema:xsd:DebitNote-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
}

#: Identificador de la referencia a la firma XMLDSig que agrega el adaptador de firma.
ID_FIRMA = "SignatureSP"

#: SUNAT publica los catálogos con este prefijo de URI en el atributo @listURI.
_PREFIJO_CATALOGO = "urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo"

#: Agencia de los códigos internacionales (UN/ECE).
UNECE = "United Nations Economic Commission for Europe"
SUNAT = "PE:SUNAT"


def catalogo(numero: str) -> str:
    """URI del catálogo SUNAT (se usa en `@listURI`)."""
    return f"{_PREFIJO_CATALOGO}{numero}"
