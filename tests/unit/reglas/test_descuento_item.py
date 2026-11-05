"""Descuento por ítem: `cac:AllowanceCharge` con `ChargeIndicator=false`.

Trazabilidad: matriz fila 32 (`/cac:InvoiceLine/cac:AllowanceCharge/cbc:Amount`) ·
`specs/domain/reglas-negocio.md` RN-05 (el descuento reduce la base antes del IGV).
"""

from __future__ import annotations

from src.dominio.comprobante import Linea
from tests.unit.generacion_xml import fabrica as f

LINEA = "cac:InvoiceLine"


def _con_descuento() -> Linea:
    return Linea.calcular(
        numero=1,
        descripcion="SACO DE ARROZ 50KG",
        unidad=f.UnidadMedida.KILOGRAMO,
        cantidad="2",
        precio_unitario="59.00",
        descuento="10.00",
    )


def test_el_descuento_reduce_el_valor_de_la_linea() -> None:
    xml = f.arbol(f.armar(f.TipoComprobante.FACTURA, "F001", (_con_descuento(),)))
    assert f.texto(xml, f"{LINEA}/cbc:LineExtensionAmount") == "90.00"


def test_el_descuento_se_declara_con_allowance_charge() -> None:
    xml = f.arbol(f.armar(f.TipoComprobante.FACTURA, "F001", (_con_descuento(),)))
    assert f.texto(xml, f"{LINEA}/cac:AllowanceCharge/cbc:ChargeIndicator") == "false"
    assert f.texto(xml, f"{LINEA}/cac:AllowanceCharge/cbc:Amount") == "10.00"
    assert f.texto(xml, f"{LINEA}/cac:AllowanceCharge/cbc:BaseAmount") == "100.00"


def test_una_linea_sin_descuento_no_declara_allowance_charge() -> None:
    xml = f.arbol(f.factura_contado())
    assert not xml.xpath(f"{LINEA}/cac:AllowanceCharge", namespaces=f.NS)
