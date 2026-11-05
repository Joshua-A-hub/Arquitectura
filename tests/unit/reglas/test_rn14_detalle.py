"""RN-14 · Detalle obligatorio: al menos una línea, cantidad positiva y descripción.

Trazabilidad: `specs/domain/reglas-negocio.md` RN-14 · matriz filas 8, 9 y 12.
"""

from __future__ import annotations

import pytest

from src.dominio.catalogos import TipoComprobante, UnidadMedida
from src.dominio.comprobante import Comprobante, Linea
from src.dominio.errores import ErrorReglaNegocio
from src.dominio.valores import Correlativo, Serie
from tests.unit.generacion_xml import fabrica as f


def test_un_comprobante_sin_lineas_se_rechaza() -> None:
    with pytest.raises(ErrorReglaNegocio) as error:
        Comprobante(
            tipo=TipoComprobante.FACTURA,
            serie=Serie("F001"),
            correlativo=Correlativo(1),
            fecha_emision=f.HOY,
            hora_emision=f.HORA,
            emisor=f.EMISOR,
            cliente=f.CLIENTE_RUC,
            lineas=(),
        )
    assert error.value.regla == "RN-14"


def test_cantidad_cero_se_rechaza() -> None:
    with pytest.raises(ErrorReglaNegocio):
        Linea.calcular(
            numero=1,
            descripcion="x",
            unidad=UnidadMedida.UNIDAD,
            cantidad="0",
            precio_unitario="1.00",
        )


def test_la_descripcion_de_la_linea_es_obligatoria() -> None:
    with pytest.raises(ErrorReglaNegocio):
        Linea.calcular(
            numero=1,
            descripcion="  ",
            unidad=UnidadMedida.UNIDAD,
            cantidad="1",
            precio_unitario="1.00",
        )


def test_line_count_numeric_coincide_con_las_lineas() -> None:
    for escenario in ("factura-contado", "factura-completa", "nota-credito"):
        xml = f.arbol(f.ESCENARIOS[escenario]())
        numero = int(f.texto(xml, "cbc:LineCountNumeric"))
        cantidad = len(
            xml.xpath("cac:InvoiceLine | cac:CreditNoteLine | cac:DebitNoteLine", namespaces=f.NS)
        )
        assert numero == cantidad, f"{escenario}: {numero} != {cantidad}"


def test_cada_linea_del_dominio_genera_su_linea_en_el_xml() -> None:
    xml = f.arbol(f.factura_completa())
    assert len(xml.xpath("cac:InvoiceLine", namespaces=f.NS)) == 7
    assert f.todos(xml, "cac:InvoiceLine/cbc:ID") == ["1", "2", "3", "4", "5", "6", "7"]


def test_la_descripcion_y_el_codigo_llegan_al_xml() -> None:
    xml = f.arbol(f.factura_contado())
    assert f.texto(xml, "cac:InvoiceLine/cac:Item/cbc:Description") == "SACO DE ARROZ 50KG"
    assert f.texto(xml, "cac:InvoiceLine/cac:Item/cac:SellersItemIdentification/cbc:ID") == "ARR-50KG"
