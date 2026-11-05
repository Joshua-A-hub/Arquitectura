"""Objetos de valor del dominio: importes, RUC, serie, correlativo y documentos.

Todo importe es `Decimal`: la coma flotante no tiene cabida en un comprobante tributario.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from src.domain.catalogos import TipoComprobante, TipoDocumentoIdentidad
from src.domain.errores import ErrorDominio, ErrorReglaNegocio

CERO = Decimal("0.00")
DOS_DECIMALES = Decimal("0.01")

# Factores del dígito verificador del RUC (RN-01)
_FACTORES_RUC = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)
_SERIE = re.compile(r"^[FB][A-Z0-9]{3}$")  # catálogo: 4 alfanuméricos (F001, FC01, BA01)
_DNI = re.compile(r"^\d{8}$")


def redondear(valor: Decimal | int | str) -> Decimal:
    """Redondeo tributario: half-up a 2 decimales (RN-08)."""
    return Decimal(str(valor)).quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)


def a_decimal(valor: Decimal | int | str) -> Decimal:
    """Convierte a `Decimal` sin pasar por `float` (protege la precisión)."""
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, float):
        raise ErrorDominio("no se admiten importes en coma flotante; usa Decimal o string")
    return Decimal(str(valor))


@dataclass(frozen=True)
class RUC:
    """RUC peruano de 11 dígitos con dígito verificador (RN-01)."""

    valor: str

    def __post_init__(self) -> None:
        if not (len(self.valor) == 11 and self.valor.isdigit()):
            raise ErrorDominio(f"el RUC debe tener 11 dígitos numéricos: {self.valor!r}")
        if not self.es_valido(self.valor):
            raise ErrorReglaNegocio("RN-01", f"el dígito verificador del RUC {self.valor} no cuadra")

    @staticmethod
    def es_valido(valor: str) -> bool:
        """Módulo 11 con factores 5,4,3,2,7,6,5,4,3,2 (10→0, 11→1)."""
        if not (len(valor) == 11 and valor.isdigit()):
            return False
        suma = sum(int(d) * f for d, f in zip(valor[:10], _FACTORES_RUC))
        resto = suma % 11
        digito = 11 - resto
        if digito == 10:
            digito = 0
        elif digito == 11:
            digito = 1
        return digito == int(valor[10])

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class Serie:
    """Serie del comprobante: 4 caracteres, el primero según el tipo (RN-10)."""

    valor: str

    def __post_init__(self) -> None:
        if not _SERIE.match(self.valor):
            raise ErrorReglaNegocio(
                "RN-10", f"serie inválida {self.valor!r}: se espera [FB] + 3 alfanuméricos (F001, FC01, BA01)"
            )

    def validar_para(self, tipo: TipoComprobante) -> None:
        """La primera letra debe corresponder al tipo de comprobante (RN-10)."""
        if tipo is TipoComprobante.FACTURA and not self.valor.startswith("F"):
            raise ErrorReglaNegocio("RN-10", f"la factura exige serie que empiece con F: {self.valor}")
        if tipo is TipoComprobante.BOLETA and not self.valor.startswith("B"):
            raise ErrorReglaNegocio("RN-10", f"la boleta exige serie que empiece con B: {self.valor}")
        if tipo.es_nota and self.valor[0] not in ("F", "B"):
            raise ErrorReglaNegocio("RN-10", f"la nota hereda serie F o B: {self.valor}")

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class Correlativo:
    """Correlativo del comprobante: entero positivo, sin huecos (RN-11)."""

    valor: int

    def __post_init__(self) -> None:
        if not isinstance(self.valor, int) or isinstance(self.valor, bool):
            raise ErrorDominio("el correlativo debe ser un entero")
        if not 1 <= self.valor <= 99_999_999:
            raise ErrorReglaNegocio("RN-11", f"correlativo fuera de rango: {self.valor}")

    def __str__(self) -> str:
        return f"{self.valor:08d}"


@dataclass(frozen=True)
class DocumentoIdentidad:
    """Documento del receptor según el catálogo 06 y las reglas de combinación (RN-02)."""

    tipo: TipoDocumentoIdentidad
    numero: str

    def __post_init__(self) -> None:
        numero = self.numero.strip()
        object.__setattr__(self, "numero", numero)
        if not numero:
            raise ErrorDominio("el número de documento es obligatorio")
        if self.tipo is TipoDocumentoIdentidad.RUC:
            RUC(numero)  # valida los 11 dígitos y el dígito verificador
        elif self.tipo is TipoDocumentoIdentidad.DNI:
            if not _DNI.match(numero):
                raise ErrorReglaNegocio("RN-02", f"el DNI debe tener 8 dígitos: {numero!r}")
        elif self.tipo is TipoDocumentoIdentidad.NO_DOMICILIADO:
            if numero != "0" and len(numero) < 8:
                raise ErrorReglaNegocio("RN-02", f"documento de no domiciliado inválido: {numero!r}")
        elif not 8 <= len(numero) <= 12:
            raise ErrorReglaNegocio("RN-02", f"documento {self.tipo.value} fuera de rango: {numero!r}")

    def validar_para(self, tipo_comprobante: TipoComprobante, *, permite_no_domiciliado: bool = False) -> None:
        """Combinación comprobante ↔ documento del receptor (RN-02).

        La factura exige RUC. La exportación admite al no domiciliado (catálogo 06 = `0`).
        """
        if tipo_comprobante is TipoComprobante.FACTURA and self.tipo is not TipoDocumentoIdentidad.RUC:
            if not (permite_no_domiciliado and self.tipo is TipoDocumentoIdentidad.NO_DOMICILIADO):
                raise ErrorReglaNegocio("RN-02", "la factura exige RUC del receptor (salvo exportación)")
        if tipo_comprobante is TipoComprobante.BOLETA and self.tipo is TipoDocumentoIdentidad.CARNET_EXTRANJERIA:
            raise ErrorReglaNegocio("RN-02", "la boleta admite DNI, RUC o consumidor final")


def formatear_importe(valor: Decimal) -> str:
    """Representación del importe en el XML: siempre 2 decimales, sin separador de miles."""
    return f"{redondear(valor):.2f}"
