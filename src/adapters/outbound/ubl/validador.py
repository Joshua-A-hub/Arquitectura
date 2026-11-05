"""Adaptador de validación: XML contra los esquemas **oficiales** de OASIS.

Se usa antes de firmar y antes de enviar (RN-18). Los esquemas viven en el repositorio:
`specs/contracts/ubl/oficial/maindoc/` + `common/`.

El parser es seguro (sin entidades externas ni acceso a red) para no exponerse a XXE.
"""

from __future__ import annotations

import threading
from pathlib import Path

from lxml import etree

from src.domain.catalogos import TipoComprobante

RAIZ = Path(__file__).resolve().parents[4]
DIR_XSD = RAIZ / "specs" / "contracts" / "ubl" / "oficial" / "maindoc"

_ARCHIVOS = {
    TipoComprobante.FACTURA: "UBL-Invoice-2.1.xsd",
    TipoComprobante.BOLETA: "UBL-Invoice-2.1.xsd",
    TipoComprobante.NOTA_CREDITO: "UBL-CreditNote-2.1.xsd",
    TipoComprobante.NOTA_DEBITO: "UBL-DebitNote-2.1.xsd",
}


def parser_seguro() -> etree.XMLParser:
    """Parser sin resolución de entidades ni red (previene XXE)."""
    return etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False, huge_tree=False)


class ValidadorXsd:
    """Implementa el puerto `IValidadorXsd`."""

    def __init__(self, directorio: Path = DIR_XSD) -> None:
        self._directorio = directorio
        self._cache: dict[str, etree.XMLSchema] = {}
        self._lock = threading.Lock()

    def _esquema(self, tipo: TipoComprobante) -> etree.XMLSchema:
        archivo = _ARCHIVOS[tipo]
        with self._lock:
            if archivo not in self._cache:
                ruta = self._directorio / archivo
                if not ruta.exists():
                    raise FileNotFoundError(
                        f"falta el esquema oficial {ruta}. "
                        "Está versionado en specs/contracts/ubl/oficial/"
                    )
                self._cache[archivo] = etree.XMLSchema(etree.parse(str(ruta)))
            return self._cache[archivo]

    def validar(self, xml: bytes, tipo: TipoComprobante) -> list[str]:
        """Devuelve la lista de errores (vacía = conforme al esquema oficial)."""
        esquema = self._esquema(tipo)
        documento = etree.fromstring(xml, parser_seguro())
        if esquema.validate(documento):
            return []
        return [f"línea {e.line}: {e.message}" for e in esquema.error_log]
