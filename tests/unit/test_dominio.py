"""Pruebas unitarias del dominio: RUC, serie, tributos, redondeo y letras."""

from __future__ import annotations

from datetime import date, time
from decimal import Decimal

import pytest

from src.domain.catalogos import AfectacionIGV, SistemaISC, TipoComprobante, UnidadMedida
from src.domain.comprobante import Cliente, Comprobante, Emisor, Linea
from src.domain.errores import ErrorReglaNegocio
from src.domain.letras import monto_en_letras
from src.domain.tributos import TASA_IGV, ConfiguracionISC, calcular_linea, redondear, valor_unitario
from src.domain.valores import RUC, Correlativo, DocumentoIdentidad, Serie
from tests.unit.generacion_xml import fabrica as f

# --- RUC (RN-01) -------------------------------------------------------------------


@pytest.mark.parametrize("ruc", ["20123456786", "20512345671", "10000000006"])
def test_ruc_con_digito_verificador_valido(ruc: str) -> None:
    assert RUC.es_valido(ruc)


@pytest.mark.parametrize("ruc", ["20123456780", "12345678901", "20A23456786", "2012345"])
def test_ruc_invalido(ruc: str) -> None:
    assert not RUC.es_valido(ruc)


def test_construir_un_ruc_invalido_lanza_regla_de_negocio() -> None:
    with pytest.raises(ErrorReglaNegocio):
        RUC("20123456780")


# --- serie y correlativo (RN-10, RN-11) ---------------------------------------------


@pytest.mark.parametrize("serie", ["F001", "FC01", "BA01", "B9Z2"])
def test_series_alfanumericas_validas(serie: str) -> None:
    Serie(serie)


@pytest.mark.parametrize("serie", ["F01", "001", "F0001", "f001"])
def test_series_invalidas(serie: str) -> None:
    with pytest.raises(ErrorReglaNegocio):
        Serie(serie)


def test_una_factura_no_puede_usar_serie_de_boleta() -> None:
    with pytest.raises(ErrorReglaNegocio):
        Serie("B001").validar_para(TipoComprobante.FACTURA)


def test_el_correlativo_se_formatea_a_ocho_digitos() -> None:
    assert str(Correlativo(123)) == "00000123"


# --- valor unitario e IGV (RN-04, RN-05) --------------------------------------------


def test_valor_unitario_gravado_descuenta_el_igv() -> None:
    assert valor_unitario(Decimal("118.00"), AfectacionIGV.GRAVADO_ONEROSA) == Decimal("100")


def test_valor_unitario_exonerado_no_descuenta_igv() -> None:
    assert valor_unitario(Decimal("118.00"), AfectacionIGV.EXONERADO_ONEROSA) == Decimal("118.00")


def test_la_tasa_de_igv_es_18_por_ciento() -> None:
    assert Decimal("0.18") == TASA_IGV


def test_igv_de_una_linea_gravada() -> None:
    linea = Linea.calcular(
        numero=1, descripcion="x", unidad=UnidadMedida.UNIDAD, cantidad="1", precio_unitario="118.00"
    )
    assert linea.tributos.valor_venta == Decimal("100.00")
    assert linea.tributos.igv == Decimal("18.00")


# --- ISC: catálogo 08 (RN-06) -------------------------------------------------------


def test_isc_ad_valorem() -> None:
    isc = ConfiguracionISC(SistemaISC.AD_VALOR, tasa=Decimal("0.25"))
    assert isc.monto(valor_venta=Decimal("100.00"), cantidad=Decimal("1"), valor_unitario=Decimal("100.00")) == Decimal(
        "25.00"
    )


def test_isc_especifico() -> None:
    isc = ConfiguracionISC(SistemaISC.MONTO_FIJO, monto_fijo=Decimal("1.35"))
    assert isc.monto(valor_venta=Decimal("0"), cantidad=Decimal("6"), valor_unitario=Decimal("0")) == Decimal("8.10")


def test_isc_al_valor() -> None:
    isc = ConfiguracionISC(SistemaISC.PRECIO_VENTA_PUBLICO, precio_venta_publico=Decimal("12.50"))
    assert isc.monto(valor_venta=Decimal("0"), cantidad=Decimal("4"), valor_unitario=Decimal("9.00")) == Decimal(
        "14.00"
    )


@pytest.mark.parametrize("sistema", [SistemaISC.AD_VALOR, SistemaISC.MONTO_FIJO, SistemaISC.PRECIO_VENTA_PUBLICO])
def test_cada_sistema_exige_su_dato(sistema: SistemaISC) -> None:
    with pytest.raises(ErrorReglaNegocio):
        ConfiguracionISC(sistema)


# --- redondeo, ICBPER y totales (RN-07, RN-08, RN-09) -------------------------------


def test_redondeo_half_up() -> None:
    assert redondear("1.005") == Decimal("1.01")
    assert redondear("1.004") == Decimal("1.00")


def test_el_igv_se_calcula_sobre_la_base_exacta() -> None:
    """Redondear la base antes de multiplicar desvía un céntimo: 8.47 x 18 % = 1.52, pero
    el tributo correcto sobre la base exacta (8.4745...) es 1.53."""
    calculado = calcular_linea(
        cantidad=Decimal("20"), precio_unitario=Decimal("0.50"), afectacion=AfectacionIGV.GRAVADO_ONEROSA
    )
    assert calculado.valor_venta == Decimal("8.47")
    assert calculado.igv == Decimal("1.53")


def test_icbper_es_un_monto_por_bolsa() -> None:
    calculado = calcular_linea(
        cantidad=Decimal("20"),
        precio_unitario=Decimal("0.50"),
        afectacion=AfectacionIGV.GRAVADO_ONEROSA,
        aplica_icbper=True,
    )
    assert calculado.icbper == Decimal("10.00")


# --- letras -------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("importe", "letras"),
    [
        ("0.00", "CERO CON 00/100 SOLES"),
        ("1.00", "UNO CON 00/100 SOLES"),
        ("21.00", "VEINTIUNO CON 00/100 SOLES"),
        ("100.00", "CIEN CON 00/100 SOLES"),
        ("530.00", "QUINIENTOS TREINTA CON 00/100 SOLES"),
        ("1000.00", "MIL CON 00/100 SOLES"),
        ("2500.50", "DOS MIL QUINIENTOS CON 50/100 SOLES"),
    ],
)
def test_importe_en_letras(importe: str, letras: str) -> None:
    assert monto_en_letras(Decimal(importe)) == letras


# --- reglas de combinación (RN-02, RN-14) -------------------------------------------


def test_factura_con_dni_se_rechaza() -> None:
    with pytest.raises(ErrorReglaNegocio):
        f.armar(
            TipoComprobante.FACTURA,
            "F001",
            (f.linea(1),),
            cliente=Cliente(DocumentoIdentidad(f.TipoDocumentoIdentidad.DNI, "45678912"), "JUAN PEREZ"),
        )


def test_la_factura_de_exportacion_admite_no_domiciliado() -> None:
    assert f.factura_exportacion_usd()


def test_un_comprobante_sin_lineas_se_rechaza() -> None:
    with pytest.raises(ErrorReglaNegocio):
        Comprobante(
            tipo=TipoComprobante.FACTURA,
            serie=Serie("F001"),
            correlativo=Correlativo(1),
            fecha_emision=date(2026, 10, 22),
            hora_emision=time(9, 0),
            emisor=Emisor(ruc=RUC("20123456786"), razon_social="ABC SAC"),
            cliente=f.CLIENTE_RUC,
            lineas=(),
        )


def test_cantidad_cero_se_rechaza() -> None:
    with pytest.raises(ErrorReglaNegocio):
        Linea.calcular(numero=1, descripcion="x", unidad=UnidadMedida.UNIDAD, cantidad="0", precio_unitario="1.00")


def test_las_cuotas_deben_sumar_el_importe_total() -> None:
    """RN-16: la suma de cuotas debe cuadrar con el total del comprobante."""
    from src.domain.catalogos import TipoFormaPago
    from src.domain.comprobante import Cuota, FormaPago

    cuotas = (Cuota(Decimal("100.00"), date(2026, 11, 21)), Cuota(Decimal("50.00"), date(2026, 12, 21)))
    with pytest.raises(ErrorReglaNegocio):
        f.armar(
            TipoComprobante.FACTURA,
            "F001",
            (f.linea(1),),  # total 210.00
            forma_pago=FormaPago(TipoFormaPago.CREDITO, cuotas),
        )


def test_cuotas_que_suman_el_total_se_aceptan() -> None:
    from src.domain.catalogos import TipoFormaPago
    from src.domain.comprobante import Cuota, FormaPago

    cuotas = (Cuota(Decimal("105.00"), date(2026, 11, 21)), Cuota(Decimal("105.00"), date(2026, 12, 21)))
    assert f.armar(
        TipoComprobante.FACTURA,
        "F001",
        (f.linea(1),),
        forma_pago=FormaPago(TipoFormaPago.CREDITO, cuotas),
    )
