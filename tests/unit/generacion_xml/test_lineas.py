"""Taller 2 · Generación: líneas del documento (cantidad, precios, orden del XSD)."""

from __future__ import annotations

import pytest

from src.domain.catalogos import UnidadMedida
from tests.unit.generacion_xml import fabrica as f

LINEAS = "cac:InvoiceLine"


def test_una_linea_por_cada_linea_del_dominio() -> None:
    xml = f.arbol(f.factura_completa())
    assert len(xml.xpath(LINEAS, namespaces=f.NS)) == 7


def test_identificador_de_cada_linea() -> None:
    xml = f.arbol(f.factura_completa())
    assert f.todos(xml, f"{LINEAS}/cbc:ID") == ["1", "2", "3", "4", "5", "6", "7"]


def test_unidad_de_medida_del_catalogo_03_por_linea() -> None:
    xml = f.arbol(f.factura_completa())
    assert f.todos(xml, f"{LINEAS}/cbc:InvoicedQuantity/@unitCode") == [
        "KGM",
        "NIU",
        "NIU",
        "NIU",
        "NIU",
        "NIU",
        "ZZ",
    ]


@pytest.mark.parametrize(
    ("unidad", "codigo"),
    [
        (UnidadMedida.UNIDAD, "NIU"),
        (UnidadMedida.KILOGRAMO, "KGM"),
        (UnidadMedida.CAJA, "BX"),
        (UnidadMedida.LITRO, "LTR"),
        (UnidadMedida.SERVICIO, "ZZ"),
        (UnidadMedida.SACO, "SA"),
    ],
)
def test_el_enum_de_unidad_llega_al_unit_code(unidad: UnidadMedida, codigo: str) -> None:
    xml = f.arbol(f.armar(f.TipoComprobante.FACTURA, "F001", (f.linea(1, unidad=unidad),)))
    assert f.texto(xml, f"{LINEAS}/cbc:InvoicedQuantity/@unitCode") == codigo


def test_cantidad_y_valor_de_venta_de_la_linea() -> None:
    xml = f.arbol(f.factura_contado())
    assert f.texto(xml, f"{LINEAS}/cbc:InvoicedQuantity") == "50"
    # 50 kg x (4.20 / 1.18) = 177.97
    assert f.texto(xml, f"{LINEAS}/cbc:LineExtensionAmount") == "177.97"


def test_precio_con_y_sin_igv_en_la_linea() -> None:
    xml = f.arbol(f.factura_contado())
    # precio de venta (con IGV) en PricingReference
    assert f.texto(xml, f"{LINEAS}/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount") == "4.20"
    assert f.texto(xml, f"{LINEAS}/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceTypeCode") == "01"
    # valor unitario (sin IGV) en Price, con 6 decimales para que cuadre con la cantidad
    assert f.texto(xml, f"{LINEAS}/cac:Price/cbc:PriceAmount") == "3.559322"


def test_el_valor_unitario_por_la_cantidad_cuadra_con_el_valor_de_venta() -> None:
    """SUNAT reconcilia `PriceAmount × cantidad` con `LineExtensionAmount`."""
    from decimal import Decimal

    xml = f.arbol(f.factura_completa())
    lineas = xml.xpath("cac:InvoiceLine", namespaces=f.NS)
    for linea in lineas:
        precio = Decimal(linea.findtext("cac:Price/cbc:PriceAmount", namespaces=f.NS))
        cantidad = Decimal(linea.findtext("cbc:InvoicedQuantity", namespaces=f.NS))
        valor = Decimal(linea.findtext("cbc:LineExtensionAmount", namespaces=f.NS))
        assert abs(precio * cantidad - valor) <= Decimal("0.01"), (
            f"línea {linea.findtext('cbc:ID', namespaces=f.NS)}: {precio} x {cantidad} != {valor}"
        )


def test_descripcion_y_codigo_del_producto() -> None:
    xml = f.arbol(f.factura_contado())
    assert f.texto(xml, f"{LINEAS}/cac:Item/cbc:Description") == "SACO DE ARROZ 50KG"
    assert f.texto(xml, f"{LINEAS}/cac:Item/cac:SellersItemIdentification/cbc:ID") == "ARR-50KG"


def test_una_linea_sin_codigo_no_lleva_identificacion_de_vendedor() -> None:
    xml = f.arbol(f.armar(f.TipoComprobante.FACTURA, "F001", (f.linea(1, codigo=None),)))
    assert not xml.xpath(f"{LINEAS}/cac:Item/cac:SellersItemIdentification", namespaces=f.NS)


def test_orden_de_los_elementos_de_la_linea_segun_el_xsd() -> None:
    """El XSD impone el orden: ID, cantidad, importe, PricingReference, TaxTotal, Item, Price."""
    xml = f.arbol(f.factura_contado())
    linea = xml.xpath(LINEAS, namespaces=f.NS)[0]
    etiquetas = [
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID",
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InvoicedQuantity",
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}LineExtensionAmount",
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PricingReference",
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal",
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Item",
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Price",
    ]
    assert [hijo.tag for hijo in linea] == etiquetas


def test_las_lineas_de_una_nota_usan_la_cantidad_correspondiente() -> None:
    xml = f.arbol(f.nota_credito())
    assert xml.xpath("cac:CreditNoteLine", namespaces=f.NS)
    assert f.texto(xml, "cac:CreditNoteLine/cbc:CreditedQuantity") == "10"


def test_line_count_numeric_coincide_con_las_lineas() -> None:
    """Control de consistencia de la matriz (fila 9)."""
    for escenario in ("factura-contado", "factura-completa", "nota-credito"):
        xml = f.arbol(f.ESCENARIOS[escenario]())
        numero = int(f.texto(xml, "cbc:LineCountNumeric"))
        cantidad = len(xml.xpath("cac:InvoiceLine | cac:CreditNoteLine | cac:DebitNoteLine", namespaces=f.NS))
        assert numero == cantidad, f"{escenario}: {numero} != {cantidad}"


def test_el_descuento_por_item_se_declara_con_allowance_charge() -> None:
    """Matriz fila 32: `/cac:InvoiceLine/cac:AllowanceCharge/cbc:Amount`."""
    from src.domain.comprobante import Linea

    con_descuento = Linea.calcular(
        numero=1,
        descripcion="SACO DE ARROZ 50KG",
        unidad=f.UnidadMedida.KILOGRAMO,
        cantidad="2",
        precio_unitario="59.00",
        descuento="10.00",
    )
    xml = f.arbol(f.armar(f.TipoComprobante.FACTURA, "F001", (con_descuento,)))
    assert f.texto(xml, f"{LINEAS}/cbc:LineExtensionAmount") == "90.00"
    assert f.texto(xml, f"{LINEAS}/cac:AllowanceCharge/cbc:ChargeIndicator") == "false"
    assert f.texto(xml, f"{LINEAS}/cac:AllowanceCharge/cbc:Amount") == "10.00"
    assert f.texto(xml, f"{LINEAS}/cac:AllowanceCharge/cbc:BaseAmount") == "100.00"


def test_una_linea_sin_descuento_no_declara_allowance_charge() -> None:
    xml = f.arbol(f.factura_contado())
    assert not xml.xpath(f"{LINEAS}/cac:AllowanceCharge", namespaces=f.NS)
