"""Cálculo tributario del dominio: IGV, ISC (tres sistemas) e ICBPER.

Reglas implementadas: RN-04 (valor unitario), RN-05 (IGV por línea), RN-06 (ISC por
sistema del catálogo 08), RN-07 (ICBPER), RN-08 (redondeo), RN-09 (totales).

Nota normativa (reglas SUNAT 3108 y 3277): la base del IGV **de la línea** incluye el
ISC, pero la base **global** del IGV (`op_gravada`) no lo incluye: es el valor de venta.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.dominio.catalogos import AfectacionIGV, SistemaISC
from src.dominio.errores import ErrorReglaNegocio
from src.dominio.valores import CERO, a_decimal, redondear

TASA_IGV = Decimal("0.18")  # 18 % vigente
TASA_ICBPER = Decimal("0.50")  # S/ 0.50 por bolsa plástica


def porcentaje_efectivo(monto: Decimal, base: Decimal) -> Decimal:
    """Tasa equivalente en % para que `base × tasa / 100 = monto` (regla SUNAT 3108).

    Se usa cuando el sistema del catálogo 08 no declara una tasa propia
    (sistema 02 específico y sistema 03 al valor).
    """
    if base == 0:
        return CERO
    return redondear(monto / base * Decimal("100"))


@dataclass(frozen=True)
class ConfiguracionISC:
    """ISC de una línea según el **catálogo 08** (sistema de cálculo).

    | Sistema | Dato obligatorio | Fórmula | Base declarada |
    |---|---|---|---|
    | `01` ad valorem | `tasa` | valor de venta × tasa | valor de venta |
    | `02` específico | `monto_fijo` | monto fijo por unidad × cantidad | valor de venta |
    | `03` al valor | `precio_venta_publico` | (PVP − valor unitario) × cantidad | PVP × cantidad |

    **Regla SUNAT 3108:** en el XML, `base × Percent / 100` debe dar el monto del ISC.
    Por eso el porcentaje se **deriva** cuando el sistema no tiene una tasa propia.
    """

    sistema: SistemaISC
    tasa: Decimal | None = None
    monto_fijo: Decimal | None = None
    precio_venta_publico: Decimal | None = None

    def __post_init__(self) -> None:
        if self.sistema is SistemaISC.AD_VALOR and (self.tasa is None or self.tasa <= 0):
            raise ErrorReglaNegocio("RN-06", "el sistema 01 (ad valorem) exige una tasa mayor que cero")
        if self.sistema is SistemaISC.MONTO_FIJO and (self.monto_fijo is None or self.monto_fijo <= 0):
            raise ErrorReglaNegocio("RN-06", "el sistema 02 (específico) exige un monto fijo mayor que cero")
        if self.sistema is SistemaISC.PRECIO_VENTA_PUBLICO and self.precio_venta_publico is None:
            raise ErrorReglaNegocio("RN-06", "el sistema 03 (al valor) exige el precio de venta al público")

    def monto(self, *, valor_venta: Decimal, cantidad: Decimal, valor_unitario: Decimal) -> Decimal:
        """ISC de la línea según el sistema del catálogo 08."""
        if self.sistema is SistemaISC.AD_VALOR:
            return redondear(valor_venta * a_decimal(self.tasa))
        if self.sistema is SistemaISC.MONTO_FIJO:
            return redondear(a_decimal(self.monto_fijo) * cantidad)
        pvp = a_decimal(self.precio_venta_publico)
        return redondear((pvp - valor_unitario) * cantidad)

    def base_impuesto(self, *, valor_venta: Decimal, cantidad: Decimal) -> Decimal:
        """Base sobre la que se declara el ISC en el XML."""
        if self.sistema is SistemaISC.PRECIO_VENTA_PUBLICO:
            return redondear(a_decimal(self.precio_venta_publico) * cantidad)
        return redondear(valor_venta)

    def porcentaje(self, *, monto: Decimal, base: Decimal) -> Decimal:
        """Porcentaje a declarar para que `base × porcentaje / 100 = monto` (regla 3108)."""
        if self.sistema is SistemaISC.AD_VALOR and self.tasa is not None:
            return (self.tasa * 100).quantize(Decimal("0.01"))
        return porcentaje_efectivo(monto, base)


@dataclass(frozen=True)
class TributosLinea:
    """Resultado del cálculo de una línea (importes ya redondeados)."""

    valor_venta: Decimal
    base_igv: Decimal
    igv: Decimal
    isc: Decimal
    icbper: Decimal
    base_isc: Decimal = CERO

    @property
    def total(self) -> Decimal:
        return redondear(self.valor_venta + self.isc + self.igv + self.icbper)


def valor_unitario(precio_unitario: Decimal, afectacion: AfectacionIGV) -> Decimal:
    """Valor de venta unitario SIN IGV (RN-04). El precio del dominio incluye IGV."""
    precio = a_decimal(precio_unitario)
    return precio if afectacion.es_gravada is False else precio / (1 + TASA_IGV)


def calcular_linea(
    *,
    cantidad: Decimal,
    precio_unitario: Decimal,
    afectacion: AfectacionIGV,
    descuento: Decimal = CERO,
    isc: ConfiguracionISC | None = None,
    aplica_icbper: bool = False,
) -> TributosLinea:
    """Calcula los tributos de una línea (RN-05, RN-06, RN-07)."""
    cantidad = a_decimal(cantidad)
    if cantidad <= 0:
        raise ErrorReglaNegocio("RN-14", "la cantidad debe ser mayor que cero")
    descuento = a_decimal(descuento)
    if descuento < 0:
        raise ErrorReglaNegocio("RN-15", "el descuento no puede ser negativo")

    unitario = valor_unitario(precio_unitario, afectacion)
    valor_exacto = unitario * cantidad - descuento
    valor_venta = redondear(valor_exacto)
    if valor_venta < 0:
        raise ErrorReglaNegocio("RN-15", "el descuento no puede superar el valor de la línea")

    monto_isc = CERO
    base_isc = CERO
    if isc is not None:
        monto_isc = isc.monto(valor_venta=valor_exacto, cantidad=cantidad, valor_unitario=unitario)
        base_isc = isc.base_impuesto(valor_venta=valor_exacto, cantidad=cantidad)

    # RN-08: el impuesto se calcula sobre la base exacta y se redondea **al final**.
    # Redondear la base antes de multiplicar desvía el IGV un céntimo (1.52 en vez de 1.53).
    base_igv_exacta = valor_exacto + monto_isc
    base_igv = redondear(base_igv_exacta)
    igv = redondear(base_igv_exacta * TASA_IGV) if afectacion.es_gravada else CERO
    icbper = redondear(TASA_ICBPER * cantidad) if aplica_icbper else CERO

    return TributosLinea(
        valor_venta=valor_venta,
        base_igv=base_igv,
        igv=igv,
        isc=monto_isc,
        icbper=icbper,
        base_isc=base_isc,
    )


@dataclass(frozen=True)
class TotalesComprobante:
    """Totales del comprobante: nunca se reciben del cliente (RN-09)."""

    op_gravada: Decimal
    op_exonerada: Decimal
    op_inafecta: Decimal
    op_exportacion: Decimal
    total_igv: Decimal
    total_isc: Decimal
    total_icbper: Decimal
    base_isc: Decimal
    importe_total: Decimal

    @property
    def valor_venta(self) -> Decimal:
        return redondear(self.op_gravada + self.op_exonerada + self.op_inafecta + self.op_exportacion)

    @property
    def total_impuestos(self) -> Decimal:
        return redondear(self.total_igv + self.total_isc + self.total_icbper)


def calcular_totales(lineas: list[tuple[AfectacionIGV, TributosLinea]]) -> TotalesComprobante:
    """Agrega las líneas ya calculadas."""
    op = {"gravada": CERO, "exonerada": CERO, "inafecta": CERO, "exportacion": CERO}
    total_igv = total_isc = total_icbper = base_isc = CERO

    for afectacion, tributos in lineas:
        if afectacion.es_gravada:
            op["gravada"] += tributos.valor_venta
        elif afectacion.value in ("20", "21"):
            op["exonerada"] += tributos.valor_venta
        elif afectacion.value in ("30", "31"):
            op["inafecta"] += tributos.valor_venta
        else:
            op["exportacion"] += tributos.valor_venta
        total_igv += tributos.igv
        total_isc += tributos.isc
        total_icbper += tributos.icbper
        # J-2: la base global del ISC solo suma las líneas que pagan ISC.
        if tributos.isc > 0:
            base_isc += tributos.base_isc

    importe = op["gravada"] + op["exonerada"] + op["inafecta"] + op["exportacion"]
    importe = importe + total_igv + total_isc + total_icbper

    return TotalesComprobante(
        op_gravada=redondear(op["gravada"]),
        op_exonerada=redondear(op["exonerada"]),
        op_inafecta=redondear(op["inafecta"]),
        op_exportacion=redondear(op["exportacion"]),
        total_igv=redondear(total_igv),
        total_isc=redondear(total_isc),
        total_icbper=redondear(total_icbper),
        base_isc=redondear(base_isc),
        importe_total=redondear(importe),
    )
