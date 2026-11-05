"""Agregado `Comprobante` y sus partes (lenguaje del dominio de ABC Software Corp).

El generador de XML recibe **estas** clases, no diccionarios ni JSON: la traducción a UBL
se hace en el adaptador, y por eso el dominio puede probarse sin HTTP ni base de datos.

Reglas que se hacen cumplir aquí: RN-02 (documento del receptor), RN-10 (serie),
RN-11 (correlativo), RN-13 (fecha), RN-14 (detalle), RN-16 (notas).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal

from src.domain.catalogos import (
    AfectacionIGV,
    Moneda,
    MotivoNotaCredito,
    MotivoNotaDebito,
    TipoComprobante,
    TipoFormaPago,
    TipoOperacion,
    UnidadMedida,
)
from src.domain.errores import ErrorReglaNegocio
from src.domain.letras import monto_en_letras
from src.domain.tributos import (
    CERO,
    ConfiguracionISC,
    TotalesComprobante,
    TributosLinea,
    calcular_linea,
    calcular_totales,
    valor_unitario,
)
from src.domain.valores import RUC, Correlativo, DocumentoIdentidad, Serie, a_decimal, redondear


@dataclass(frozen=True)
class Emisor:
    """Empresa que emite el comprobante."""

    ruc: RUC
    razon_social: str
    nombre_comercial: str = ""
    ubigeo: str = "150101"
    direccion: str = ""
    codigo_establecimiento: str = "0000"

    def __post_init__(self) -> None:
        if len(self.razon_social.strip()) < 3:
            raise ErrorReglaNegocio("RN-03", "la razón social del emisor es obligatoria")
        if not (len(self.ubigeo) == 6 and self.ubigeo.isdigit()):
            raise ErrorReglaNegocio("RN-03", f"ubigeo inválido: {self.ubigeo!r}")


@dataclass(frozen=True)
class Cliente:
    """Receptor del comprobante."""

    documento: DocumentoIdentidad
    razon_social: str
    direccion: str = ""
    ubigeo: str = ""

    def __post_init__(self) -> None:
        if len(self.razon_social.strip()) < 3:
            raise ErrorReglaNegocio("RN-03", "la razón social del cliente es obligatoria")


@dataclass(frozen=True)
class Linea:
    """Línea del comprobante, ya calculada.

    `precio_unitario` es el precio de venta **con IGV**; el valor unitario se deriva (RN-04).
    """

    numero: int
    descripcion: str
    unidad: UnidadMedida
    cantidad: Decimal
    valor_unitario: Decimal
    precio_unitario: Decimal
    afectacion: AfectacionIGV
    codigo_producto: str | None = None
    descuento: Decimal = CERO
    isc: ConfiguracionISC | None = None
    aplica_icbper: bool = False
    tributos: TributosLinea = field(init=False)

    def __post_init__(self) -> None:
        if not self.descripcion.strip():
            raise ErrorReglaNegocio("RN-14", "cada línea exige descripción")
        calculado = calcular_linea(
            cantidad=self.cantidad,
            precio_unitario=self.precio_unitario,
            afectacion=self.afectacion,
            descuento=self.descuento,
            isc=self.isc,
            aplica_icbper=self.aplica_icbper,
        )
        object.__setattr__(self, "tributos", calculado)

    @classmethod
    def calcular(
        cls,
        *,
        numero: int,
        descripcion: str,
        unidad: UnidadMedida,
        cantidad: Decimal | str,
        precio_unitario: Decimal | str,
        afectacion: AfectacionIGV = AfectacionIGV.GRAVADO_ONEROSA,
        codigo_producto: str | None = None,
        descuento: Decimal | str = CERO,
        isc: ConfiguracionISC | None = None,
        aplica_icbper: bool = False,
    ) -> Linea:
        """Construye la línea calculando el valor unitario a partir del precio con IGV."""
        precio = a_decimal(precio_unitario)
        return cls(
            numero=numero,
            descripcion=descripcion,
            unidad=unidad,
            cantidad=a_decimal(cantidad),
            valor_unitario=valor_unitario(precio, afectacion),
            precio_unitario=precio,
            afectacion=afectacion,
            codigo_producto=codigo_producto,
            descuento=a_decimal(descuento),
            isc=isc,
            aplica_icbper=aplica_icbper,
        )

    @property
    def valor_venta(self) -> Decimal:
        return self.tributos.valor_venta

    @property
    def total(self) -> Decimal:
        return self.tributos.total


@dataclass(frozen=True)
class Cuota:
    """Cuota de una venta al crédito."""

    monto: Decimal
    fecha_vencimiento: date

    def __post_init__(self) -> None:
        if a_decimal(self.monto) <= 0:
            raise ErrorReglaNegocio("RN-16", "cada cuota debe tener un monto mayor que cero")


@dataclass(frozen=True)
class FormaPago:
    """Contado o crédito con cuotas (RS 193-2020)."""

    tipo: TipoFormaPago
    cuotas: tuple[Cuota, ...] = ()

    def __post_init__(self) -> None:
        if self.tipo is TipoFormaPago.CREDITO and not self.cuotas:
            raise ErrorReglaNegocio("RN-16", "la forma de pago al crédito exige al menos una cuota")
        if self.tipo is TipoFormaPago.CONTADO and self.cuotas:
            raise ErrorReglaNegocio("RN-16", "la forma de pago al contado no admite cuotas")


@dataclass(frozen=True)
class Comprobante:
    """Raíz del agregado: protege sus líneas, sus totales y su numeración."""

    tipo: TipoComprobante
    serie: Serie
    correlativo: Correlativo
    fecha_emision: date
    hora_emision: time
    emisor: Emisor
    cliente: Cliente
    lineas: tuple[Linea, ...]
    moneda: Moneda = Moneda.PEN
    tipo_operacion: TipoOperacion = TipoOperacion.VENTA_INTERNA
    forma_pago: FormaPago | None = None
    referencia: Comprobante | None = None
    motivo: MotivoNotaCredito | MotivoNotaDebito | None = None
    sustento: str | None = None
    documentos_legado: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # RN-14: al menos una línea
        if not self.lineas:
            raise ErrorReglaNegocio("RN-14", "el comprobante exige al menos una línea")
        # RN-10: serie coherente con el tipo
        self.serie.validar_para(self.tipo)
        # RN-02: documento del receptor según el comprobante.
        # La factura exige RUC, salvo la exportación, que admite al no domiciliado (catálogo 06 = 0).
        self.cliente.documento.validar_para(
            self.tipo, permite_no_domiciliado=self.tipo_operacion is TipoOperacion.EXPORTACION
        )
        # RN-13: fecha no futura
        if self.fecha_emision > date(2026, 11, 5):
            raise ErrorReglaNegocio("RN-13", f"la fecha de emisión no puede ser futura: {self.fecha_emision}")
        # RN-16: las notas exigen referencia y motivo
        if self.tipo.es_nota and (self.referencia is None or self.motivo is None):
            raise ErrorReglaNegocio("RN-16", "la nota exige comprobante de referencia y motivo")
        if self.tipo.es_nota and self.referencia is not None and self.referencia.tipo.es_nota:
            raise ErrorReglaNegocio("RN-16", "una nota no puede referenciar otra nota")
        if not self.tipo.es_nota and self.motivo is not None:
            raise ErrorReglaNegocio("RN-16", "solo las notas llevan motivo de catálogo 09/10")
        # RN-16: si hay cuotas, deben sumar exactamente el importe total
        if self.forma_pago is not None and self.forma_pago.cuotas:
            suma = sum((cuota.monto for cuota in self.forma_pago.cuotas), CERO)
            if redondear(suma) != self.totales.importe_total:
                raise ErrorReglaNegocio(
                    "RN-16",
                    f"las cuotas suman {redondear(suma)} y el total del comprobante es {self.totales.importe_total}",
                )

    # --- derivados -----------------------------------------------------------------
    @property
    def serie_numero(self) -> str:
        """Identificador SUNAT del comprobante: `F001-00000123` (mapea a `cbc:ID`)."""
        return f"{self.serie}-{self.correlativo}"

    @property
    def totales(self) -> TotalesComprobante:
        return calcular_totales([(linea.afectacion, linea.tributos) for linea in self.lineas])

    @property
    def monto_en_letras(self) -> str:
        return monto_en_letras(self.totales.importe_total, self.moneda)

    @property
    def importe_total(self) -> Decimal:
        return self.totales.importe_total

    def resumen(self) -> dict[str, str]:
        """Resumen legible (lo usan la CLI y las pruebas de evidencia)."""
        return {
            "serie_numero": self.serie_numero,
            "tipo": self.tipo.value,
            "moneda": self.moneda.value,
            "valor_venta": f"{self.totales.valor_venta:.2f}",
            "igv": f"{self.totales.total_igv:.2f}",
            "isc": f"{self.totales.total_isc:.2f}",
            "icbper": f"{self.totales.total_icbper:.2f}",
            "importe_total": f"{redondear(self.totales.importe_total):.2f}",
        }
