"""RN-02 · Documento del receptor según el tipo de comprobante (catálogo 06).

Trazabilidad: `specs/domain/reglas-negocio.md` RN-02 · matriz fila 19
(`cac:AccountingCustomerParty/.../cbc:ID/@schemeID`).
"""

from __future__ import annotations

import pytest

from src.dominio.catalogos import TipoComprobante, TipoDocumentoIdentidad, TipoOperacion
from src.dominio.comprobante import Cliente
from src.dominio.errores import ErrorReglaNegocio
from src.dominio.valores import DocumentoIdentidad
from tests.unit.generacion_xml import fabrica as f


def test_factura_exige_ruc_del_receptor() -> None:
    with pytest.raises(ErrorReglaNegocio) as error:
        f.armar(
            TipoComprobante.FACTURA,
            "F001",
            (f.linea(1),),
            cliente=Cliente(DocumentoIdentidad(TipoDocumentoIdentidad.DNI, "45678912"), "JUAN PEREZ"),
        )
    assert error.value.regla == "RN-02"


def test_boleta_admite_dni() -> None:
    assert f.armar(TipoComprobante.BOLETA, "B001", (f.linea(1),), cliente=f.CLIENTE_DNI)


def test_boleta_admite_consumidor_final() -> None:
    cliente = Cliente(DocumentoIdentidad(TipoDocumentoIdentidad.NO_DOMICILIADO, "0"), "CLIENTES VARIOS")
    assert f.armar(TipoComprobante.BOLETA, "B001", (f.linea(1),), cliente=cliente)


def test_la_exportacion_admite_no_domiciliado() -> None:
    assert f.factura_exportacion_usd()


def test_la_exportacion_sigue_exigiendo_no_domiciliado() -> None:
    with pytest.raises(ErrorReglaNegocio):
        f.armar(
            TipoComprobante.FACTURA,
            "F002",
            (f.linea(1),),
            cliente=Cliente(DocumentoIdentidad(TipoDocumentoIdentidad.DNI, "45678912"), "JUAN PEREZ"),
            tipo_operacion=TipoOperacion.EXPORTACION,
        )


def test_el_dni_debe_tener_ocho_digitos() -> None:
    with pytest.raises(ErrorReglaNegocio):
        DocumentoIdentidad(TipoDocumentoIdentidad.DNI, "123")


@pytest.mark.parametrize(
    ("escenario", "scheme"),
    [("factura-contado", "6"), ("boleta", "1"), ("factura-exportacion-usd", "0")],
)
def test_el_scheme_id_del_receptor_sale_del_catalogo_06(escenario: str, scheme: str) -> None:
    xml = f.arbol(f.ESCENARIOS[escenario]())
    cliente = "cac:AccountingCustomerParty/cac:Party"
    assert f.texto(xml, f"{cliente}/cac:PartyIdentification/cbc:ID/@schemeID") == scheme
    assert f.texto(xml, f"{cliente}/cac:PartyIdentification/cbc:ID/@schemeURI").endswith("catalogo06")
