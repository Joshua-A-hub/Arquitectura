"""Puertos del dominio (arquitectura hexagonal).

**Fase 1:** los contratos se definieron antes del código.
**Taller 2:** ya están implementados los dos adaptadores de salida del XML:

    src/adaptadores/salida/ubl/generador.py   -> IXmlBuilder   (dominio → clases del XSD → XML)
    src/adaptadores/salida/ubl/validador.py   -> IValidadorXsd (XML contra el esquema oficial)

Pendientes (fase siguiente): `IComprobanteRepository`, `IFirmaDigital`, `ISunatGateway` y los
servicios de entrada. Los puertos de persistencia siguen hablando de datos (`dict`) porque la
persistencia no forma parte de esta entrega.

Regla: el dominio importa estas interfaces; los adaptadores las implementan. Nunca al revés.
"""

from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable

from src.dominio.catalogos import TipoComprobante
from src.dominio.comprobante import Comprobante

# --------------------------------------------------------------------------- #
# Tipos de apoyo (contratos de datos, sin comportamiento)
# --------------------------------------------------------------------------- #


class Cdr:
    """Constancia de Recepción devuelta por SUNAT/OSE (código 0 = aceptado)."""

    codigo: str
    descripcion: str
    fecha_recepcion: str


class FiltroComprobantes:
    """Criterios de búsqueda del listado."""

    tipo: str | None = None
    estado: str | None = None
    desde: date | None = None
    hasta: date | None = None


# --------------------------------------------------------------------------- #
# Puertos de entrada: lo que el dominio ofrece al exterior
# --------------------------------------------------------------------------- #


@runtime_checkable
class IEmisionService(Protocol):
    """Caso de uso: emitir un comprobante a partir de un comando validado."""

    def emitir(self, comando: dict) -> dict:
        """Valida reglas, calcula totales, genera y firma el XML, envía y guarda el CDR."""
        ...

    def consultar(self, numero: str) -> dict | None:
        """Devuelve el comprobante por su número (`F001-00000123`)."""
        ...


@runtime_checkable
class INotaService(Protocol):
    """Caso de uso: emitir nota de crédito o débito sobre un comprobante aceptado."""

    def emitir_nota(self, id_comprobante: str, comando: dict) -> dict: ...


@runtime_checkable
class IMigracionService(Protocol):
    """Caso de uso: migrar fichas del sistema legado conservando trazabilidad."""

    def migrar(self, fichas: list[dict]) -> dict:
        """Devuelve total, migradas, observadas y el detalle por ficha (RN-21..RN-24)."""
        ...


# --------------------------------------------------------------------------- #
# Puertos de salida: lo que el dominio necesita del exterior
# --------------------------------------------------------------------------- #


@runtime_checkable
class IComprobanteRepository(Protocol):
    """Persistencia de comprobantes y asignación de correlativos."""

    def siguiente_numero(self, tipo: str, serie: str) -> tuple[str, int]:
        """Asigna el correlativo de forma atómica. Devuelve (serie_numero, correlativo)."""
        ...

    def guardar(self, comprobante: dict) -> None: ...

    def obtener(self, numero: str) -> dict | None: ...

    def listar(self, filtro: FiltroComprobantes) -> list[dict]: ...


@runtime_checkable
class IXmlBuilder(Protocol):
    """Construye el documento UBL 2.1 a partir del **agregado del dominio**.

    Implementado por `src/adaptadores/salida/ubl/generador.py` con las clases que `xsdata`
    produce desde el XSD oficial (ver ADR-0004).
    """

    def construir(self, comprobante: Comprobante) -> bytes:
        """Devuelve el XML del comprobante, sin firmar y conforme al esquema oficial."""
        ...


@runtime_checkable
class IFirmaDigital(Protocol):
    """Firma el XML con el certificado del emisor (XMLDSig).

    Implementado por `src/adaptadores/salida/firma/xmldsig.py`.
    """

    def firmar(self, xml: bytes) -> bytes:
        """Devuelve el XML firmado. El certificado nunca sale del servidor."""
        ...


@runtime_checkable
class ISunatGateway(Protocol):
    """Comunicación con la OSE o SUNAT."""

    def enviar(self, xml_firmado: bytes) -> Cdr:
        """Envía el comprobante y devuelve el CDR (RN-19)."""
        ...


@runtime_checkable
class IValidadorXsd(Protocol):
    """Validación formal contra el **esquema oficial** de OASIS (RN-18).

    Implementado por `src/adaptadores/salida/ubl/validador.py`.
    """

    def validar(self, xml: bytes, tipo: TipoComprobante) -> list[str]:
        """Devuelve los errores del esquema (vacía = conforme)."""
        ...
