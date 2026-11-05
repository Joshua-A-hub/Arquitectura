"""Verificación de la fase 1: el dominio calcula lo que dicen las reglas.

Reproduce el comprobante de ejemplo de la entrega (F001-00000123) y comprueba que los
totales coinciden con `specs/contracts/dto/ejemplo-comprobante-response.json`:
449.83 + 70.17 + 10.00 = 530.00.

Uso:  python validacion/verificar_dominio.py
"""

from __future__ import annotations

import sys
from datetime import date, time
from decimal import Decimal

from src.domain.catalogos import (
    AfectacionIGV,
    Moneda,
    SistemaISC,
    TipoComprobante,
    TipoDocumentoIdentidad,
    UnidadMedida,
)
from src.domain.comprobante import Cliente, Comprobante, Emisor, Linea
from src.domain.errores import ErrorDominio, ErrorReglaNegocio
from src.domain.letras import monto_en_letras
from src.domain.tributos import ConfiguracionISC
from src.domain.valores import RUC, Correlativo, DocumentoIdentidad, Serie

ok: list[str] = []
fallos: list[str] = []


def comprobar(condicion: bool, mensaje_ok: str, mensaje_fallo: str) -> None:
    (ok if condicion else fallos).append(mensaje_ok if condicion else mensaje_fallo)


def ejemplo() -> Comprobante:
    emisor = Emisor(ruc=RUC("20123456786"), razon_social="ABC SOFTWARE CORP SAC", direccion="AV. COLONIAL 456")
    cliente = Cliente(DocumentoIdentidad(TipoDocumentoIdentidad.RUC, "20512345671"), "DISTRIBUIDORA SELVA SAC")
    lineas = (
        Linea.calcular(
            numero=1, descripcion="SACO DE ARROZ 50KG", unidad=UnidadMedida.UNIDAD,
            cantidad="10", precio_unitario="45.00", codigo_producto="ARR-50KG",
        ),
        Linea.calcular(
            numero=2, descripcion="CAJA DE LECHE 1L", unidad=UnidadMedida.CAJA,
            cantidad="5", precio_unitario="12.00", codigo_producto="LEC-1L",
            afectacion=AfectacionIGV.EXONERADO_ONEROSA,
        ),
        Linea.calcular(
            numero=3, descripcion="BOLSA PLASTICA RECICLABLE", unidad=UnidadMedida.UNIDAD,
            cantidad="20", precio_unitario="0.50", codigo_producto="BOL-001", aplica_icbper=True,
        ),
    )
    return Comprobante(
        tipo=TipoComprobante.FACTURA, serie=Serie("F001"), correlativo=Correlativo(123),
        fecha_emision=date(2026, 10, 22), hora_emision=time(9, 15), emisor=emisor,
        cliente=cliente, lineas=lineas,
    )


def main() -> int:
    # 1. RUC (RN-01)
    comprobar(RUC.es_valido("20123456786"), "el RUC 20123456786 pasa el módulo 11", "el RUC de ABC debería validar")
    comprobar(not RUC.es_valido("20123456780"), "un RUC con dígito alterado se rechaza", "se aceptó un RUC inválido")
    try:
        RUC("12345678901")
        fallos.append("se construyó un RUC inválido sin lanzar error")
    except ErrorReglaNegocio:
        ok.append("el RUC inválido lanza ErrorReglaNegocio (RN-01)")

    # 2. Serie alfanumérica (RN-10)
    for serie in ("F001", "FC01", "BA01", "B9Z2"):
        try:
            Serie(serie)
            ok.append(f"la serie alfanumérica {serie} se acepta")
        except ErrorDominio:
            fallos.append(f"la serie alfanumérica {serie} fue rechazada")
    try:
        Serie("F01")
        fallos.append("la serie de 3 caracteres 'F01' fue aceptada")
    except ErrorReglaNegocio:
        ok.append("la serie 'F01' se rechaza (debe tener 4 caracteres)")

    # 3. El comprobante de ejemplo de la entrega
    c = ejemplo()
    t = c.totales
    comprobar(c.serie_numero == "F001-00000123", f"serie_numero = {c.serie_numero}", f"serie_numero inesperado: {c.serie_numero}")
    comprobar(t.op_gravada == Decimal("389.83"), f"op_gravada = {t.op_gravada}", f"op_gravada {t.op_gravada} != 389.83")
    comprobar(t.op_exonerada == Decimal("60.00"), f"op_exonerada = {t.op_exonerada}", f"op_exonerada {t.op_exonerada} != 60.00")
    comprobar(t.valor_venta == Decimal("449.83"), f"valor de venta = {t.valor_venta}", f"valor de venta {t.valor_venta} != 449.83")
    comprobar(t.total_igv == Decimal("70.17"), f"IGV total = {t.total_igv}", f"IGV {t.total_igv} != 70.17")
    comprobar(t.total_icbper == Decimal("10.00"), f"ICBPER total = {t.total_icbper}", f"ICBPER {t.total_icbper} != 10.00")
    comprobar(t.importe_total == Decimal("530.00"), f"importe total = {t.importe_total}", f"importe {t.importe_total} != 530.00")

    # 4. Importe en letras (leyenda 1000)
    esperado = "QUINIENTOS TREINTA CON 00/100 SOLES"
    comprobar(c.monto_en_letras == esperado, f"letras: {c.monto_en_letras}", f"letras inesperadas: {c.monto_en_letras}")
    for importe, letras in (
        ("1.00", "UNO CON 00/100 SOLES"),
        ("21.00", "VEINTIUNO CON 00/100 SOLES"),
        ("100.00", "CIEN CON 00/100 SOLES"),
        ("1000.00", "MIL CON 00/100 SOLES"),
        ("118.50", "CIENTO DIECIOCHO CON 50/100 SOLES"),
        ("1000000.00", "UN MILLÓN CON 00/100 SOLES"),
    ):
        obtenido = monto_en_letras(Decimal(importe), Moneda.PEN)
        comprobar(obtenido == letras, f"letras {importe} = {obtenido}", f"letras {importe}: {obtenido!r} != {letras!r}")

    # 5. ISC: los tres sistemas del catálogo 08 (RN-06)
    ad_valorem = ConfiguracionISC(SistemaISC.AD_VALOR, tasa=Decimal("0.25"))
    comprobar(ad_valorem.monto(valor_venta=Decimal("100.00"), cantidad=Decimal("5"), valor_unitario=Decimal("20.00")) == Decimal("25.00"),
              "ISC sistema 01 (ad valorem) = 25.00", "ISC sistema 01 incorrecto")
    especifico = ConfiguracionISC(SistemaISC.MONTO_FIJO, monto_fijo=Decimal("1.35"))
    comprobar(especifico.monto(valor_venta=Decimal("100.00"), cantidad=Decimal("6"), valor_unitario=Decimal("20.00")) == Decimal("8.10"),
              "ISC sistema 02 (específico) = 8.10", "ISC sistema 02 incorrecto")
    al_valor = ConfiguracionISC(SistemaISC.PRECIO_VENTA_PUBLICO, precio_venta_publico=Decimal("12.50"))
    comprobar(al_valor.monto(valor_venta=Decimal("100.00"), cantidad=Decimal("4"), valor_unitario=Decimal("9.00")) == Decimal("14.00"),
              "ISC sistema 03 (al valor) = 14.00", "ISC sistema 03 incorrecto")
    try:
        ConfiguracionISC(SistemaISC.MONTO_FIJO)
        fallos.append("el sistema 02 sin monto fijo fue aceptado")
    except ErrorReglaNegocio:
        ok.append("el sistema 02 sin monto fijo se rechaza (RN-06)")

    # 6. IGV sobre valor + ISC y base global sin ISC (reglas 3108 / 3277)
    linea_isc = Linea.calcular(
        numero=1, descripcion="CERVEZA BOTELLA 620 ML", unidad=UnidadMedida.UNIDAD,
        cantidad="12", precio_unitario="8.00", isc=ConfiguracionISC(SistemaISC.AD_VALOR, tasa=Decimal("0.25")),
    )
    valor = linea_isc.valor_venta
    isc = linea_isc.tributos.isc
    comprobar(isc == Decimal("20.34"), f"ISC de la cerveza = {isc}", f"ISC de la cerveza {isc} != 20.34")
    comprobar(linea_isc.tributos.base_igv == valor + isc, "la base del IGV de la línea incluye el ISC (regla 3108)",
              "la base del IGV de la línea no incluye el ISC")
    comprobar(linea_isc.tributos.igv == Decimal("18.31"), f"IGV de la cerveza = {linea_isc.tributos.igv}",
              f"IGV de la cerveza {linea_isc.tributos.igv} != 18.31")
    totales_isc = c.__class__(
        tipo=c.tipo, serie=c.serie, correlativo=c.correlativo, fecha_emision=c.fecha_emision,
        hora_emision=c.hora_emision, emisor=c.emisor, cliente=c.cliente, lineas=(linea_isc,),
    ).totales
    comprobar(totales_isc.op_gravada == valor, "la base global del IGV NO incluye el ISC (regla 3277)",
              "la base global del IGV incluye el ISC")

    # 7. RN-02: factura con DNI se rechaza
    try:
        Comprobante(
            tipo=TipoComprobante.FACTURA, serie=Serie("F001"), correlativo=Correlativo(1),
            fecha_emision=date(2026, 10, 22), hora_emision=time(9, 15), emisor=c.emisor,
            cliente=Cliente(DocumentoIdentidad(TipoDocumentoIdentidad.DNI, "45678912"), "JUAN PEREZ"),
            lineas=(Linea.calcular(numero=1, descripcion="X", unidad=UnidadMedida.UNIDAD, cantidad="1", precio_unitario="10.00"),),
        )
        fallos.append("se emitió una factura con DNI (RN-02)")
    except ErrorReglaNegocio:
        ok.append("una factura a cliente con DNI se rechaza (RN-02)")

    print("=" * 74)
    print(" VERIFICACIÓN DEL DOMINIO (cálculos y reglas)")
    print("=" * 74)
    for linea in ok:
        print("  OK   ", linea)
    for linea in fallos:
        print("  FALLA", linea)
    print("-" * 74)
    print(f"  {len(ok)} comprobaciones correctas, {len(fallos)} fallos")
    return 0 if not fallos else 1


if __name__ == "__main__":
    sys.exit(main())
