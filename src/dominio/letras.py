"""Importe en letras para la leyenda 1000 del comprobante.

SUNAT exige la leyenda `cbc:Note[@languageLocaleID='1000']` con el importe en letras:
`QUINIENTOS TREINTA CON 00/100 SOLES`.
"""

from __future__ import annotations

from decimal import Decimal

from src.dominio.catalogos import Moneda
from src.dominio.valores import redondear

_UNIDADES = (
    "CERO",
    "UNO",
    "DOS",
    "TRES",
    "CUATRO",
    "CINCO",
    "SEIS",
    "SIETE",
    "OCHO",
    "NUEVE",
    "DIEZ",
    "ONCE",
    "DOCE",
    "TRECE",
    "CATORCE",
    "QUINCE",
    "DIECISÉIS",
    "DIECISIETE",
    "DIECIOCHO",
    "DIECINUEVE",
    "VEINTE",
)
_DECENAS = {
    30: "TREINTA",
    40: "CUARENTA",
    50: "CINCUENTA",
    60: "SESENTA",
    70: "SETENTA",
    80: "OCHENTA",
    90: "NOVENTA",
}
_CENTENAS = {
    1: "CIENTO",
    2: "DOSCIENTOS",
    3: "TRESCIENTOS",
    4: "CUATROCIENTOS",
    5: "QUINIENTOS",
    6: "SEISCIENTOS",
    7: "SETECIENTOS",
    8: "OCHOCIENTOS",
    9: "NOVECIENTOS",
}


def _hasta_99(n: int, apocope: bool = False) -> str:
    if n <= 20:
        if apocope and n == 1:
            return "UN"
        return _UNIDADES[n]
    if n < 30:
        resto = n - 20
        if resto == 0:
            return "VEINTE"
        if resto == 1 and apocope:
            return "VEINTIÚN"
        return "VEINTI" + _UNIDADES[resto]
    decena, unidad = divmod(n, 10)
    texto = _DECENAS[decena * 10]
    if unidad:
        texto += " Y " + _UNIDADES[unidad]
    return texto


def _hasta_999(n: int, apocope: bool = False) -> str:
    if n == 100:
        return "CIEN"
    centena, resto = divmod(n, 100)
    partes = []
    if centena:
        partes.append(_CENTENAS[centena])
    if resto:
        partes.append(_hasta_99(resto, apocope=apocope))
    return " ".join(partes)


def _entero_en_letras(n: int) -> str:
    if n == 0:
        return "CERO"
    if n > 999_999_999:
        raise ValueError("el importe en letras solo cubre hasta 999 999 999.99")

    partes: list[str] = []
    millones, resto = divmod(n, 1_000_000)
    miles, unidades = divmod(resto, 1000)

    if millones:
        partes.append("UN MILLÓN" if millones == 1 else f"{_hasta_999(millones, apocope=True)} MILLONES")
    if miles:
        partes.append("MIL" if miles == 1 else f"{_hasta_999(miles, apocope=True)} MIL")
    if unidades:
        partes.append(_hasta_999(unidades, apocope=False))
    return " ".join(partes)


def monto_en_letras(importe: Decimal, moneda: Moneda = Moneda.PEN) -> str:
    """`530.00` → `QUINIENTOS TREINTA CON 00/100 SOLES`."""
    total = redondear(importe)
    entero = int(total)
    centavos = int((total - entero) * 100)
    return f"{_entero_en_letras(entero)} CON {centavos:02d}/100 {moneda.nombre}"
