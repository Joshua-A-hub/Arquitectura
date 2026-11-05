"""RN-06 · ISC con los tres sistemas del catálogo 08.

Verifica las reglas SUNAT que un XML con ISC debe cumplir y que el corrector marcó:
  * **J-1 / 3108**: `base × Percent / 100 == TaxAmount` en los tres sistemas.
  * **J-2**: la base global del ISC suma solo las líneas que pagan ISC.
  * **J-3**: el sistema 03 declara como base el PVP de la línea.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-06 · matriz fila 38 (ISC) y 41 (total ISC).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests.unit.generacion_xml import fabrica as f

NS = f.NS
LINEA = "cac:InvoiceLine[{n}]"


def _subtotal_isc(xml, n: int):
    """Devuelve el TaxSubtotal del tributo 2000 (ISC) de la línea n."""
    candidatos = xml.xpath(
        f"{LINEA.format(n=n)}/cac:TaxTotal/cac:TaxSubtotal"
        "[cac:TaxCategory/cac:TaxScheme/cbc:ID='2000']",
        namespaces=NS,
    )
    assert candidatos, f"la línea {n} no declara ISC"
    return candidatos[0]


def _path(nodo, ruta: str) -> str:
    resultado = nodo.xpath(ruta, namespaces=NS)
    return resultado[0] if isinstance(resultado[0], str) else (resultado[0].text or "")


@pytest.mark.parametrize(
    ("linea", "sistema"),
    [(2, "02"), (3, "01"), (4, "03")],
)
def test_el_isc_declara_tier_range_del_catalogo_08(linea: int, sistema: str) -> None:
    xml = f.arbol(f.factura_completa())
    subtotal = _subtotal_isc(xml, linea)
    assert _path(subtotal, "cac:TaxCategory/cbc:TierRange") == sistema
    assert _path(subtotal, "cac:TaxCategory/cac:TaxScheme/cbc:ID") == "2000"


@pytest.mark.parametrize("linea", [2, 3, 4])
def test_la_base_por_la_tasa_da_el_monto_del_isc(linea: int) -> None:
    """Regla SUNAT 3108: base × Percent / 100 = TaxAmount (J-1 y J-3)."""
    xml = f.arbol(f.factura_completa())
    subtotal = _subtotal_isc(xml, linea)
    base = Decimal(_path(subtotal, "cbc:TaxableAmount"))
    porcentaje = Decimal(_path(subtotal, "cac:TaxCategory/cbc:Percent"))
    monto = Decimal(_path(subtotal, "cbc:TaxAmount"))
    assert porcentaje > 0, "el ISC debe declarar un porcentaje"
    assert abs(base * porcentaje / Decimal("100") - monto) <= Decimal("0.01")


def test_el_sistema_02_informa_la_tasa_equivalente() -> None:
    """J-1: el pisco es monto fijo; el XML debe llevar un Percent que cuadre."""
    xml = f.arbol(f.factura_completa())
    subtotal = _subtotal_isc(xml, 2)
    base = Decimal(_path(subtotal, "cbc:TaxableAmount"))  # 270.00
    monto = Decimal(_path(subtotal, "cbc:TaxAmount"))  # 8.10
    porcentaje = Decimal(_path(subtotal, "cac:TaxCategory/cbc:Percent"))
    assert porcentaje == (monto / base * 100).quantize(Decimal("0.01"))
    assert _path(subtotal, "cac:TaxCategory/cbc:PerUnitAmount") == "1.35"


def test_el_sistema_03_declara_como_base_el_precio_de_venta_al_publico() -> None:
    """J-3: gaseosa — 4 unidades × PVP 12.50 = base 50.00 (no el valor de venta 36.00)."""
    xml = f.arbol(f.factura_completa())
    subtotal = _subtotal_isc(xml, 4)
    assert Decimal(_path(subtotal, "cbc:TaxableAmount")) == Decimal("50.00")


def test_la_base_global_del_isc_solo_suma_lineas_con_isc() -> None:
    """J-2: la base global del ISC excluye exoneradas e inafectas.

    Con J-3 corregido, la base de cada línea es: valor de venta (sistemas 01 y 02) o
    PVP × cantidad (sistema 03). La base global es la suma de esas bases, no el valor
    de venta de todo el comprobante (que incluía líneas sin ISC).
    """
    comprobante = f.factura_completa()
    xml = f.arbol(comprobante)

    doc = xml.xpath(
        "cac:TaxTotal/cac:TaxSubtotal[cac:TaxCategory/cac:TaxScheme/cbc:ID='2000']",
        namespaces=NS,
    )[0]
    base_global = Decimal(_path(doc, "cbc:TaxableAmount"))

    suma_bases = sum(
        (linea.tributos.base_isc for linea in comprobante.lineas if linea.tributos.isc > 0),
        start=Decimal("0.00"),
    )
    assert base_global == suma_bases
    # La suma incluye solo las 3 líneas con ISC; el valor de venta de todo el
    # comprobante (que sumaba las 7 líneas) es mayor.
    assert base_global < comprobante.totales.valor_venta
    assert base_global == Decimal("401.36")
