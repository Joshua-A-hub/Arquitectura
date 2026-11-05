"""Catálogos SUNAT del dominio (lenguaje ubicuo).

Cada enumeración corresponde a un catálogo oficial y sus códigos son los que viajan al XML.
El generador **no** decide códigos: los toma de aquí.

| Clase | Catálogo | Dónde se usa en el UBL |
|---|---|---|
| `TipoComprobante` | 01 | raíz del documento + `cbc:InvoiceTypeCode` |
| `Moneda` | 02 | `cbc:DocumentCurrencyCode` y `@currencyID` |
| `UnidadMedida` | 03 | `cbc:InvoicedQuantity/@unitCode` |
| `Tributo` | 05 | `cac:TaxScheme/cbc:ID` |
| `TipoDocumentoIdentidad` | 06 | `cac:PartyIdentification/cbc:ID/@schemeID` |
| `AfectacionIGV` | 07 | `cbc:TaxExemptionReasonCode` |
| `SistemaISC` | 08 | `cbc:TierRange` |
| `MotivoNotaCredito` | 09 | `cac:DiscrepancyResponse/cbc:ResponseCode` |
| `MotivoNotaDebito` | 10 | `cac:DiscrepancyResponse/cbc:ResponseCode` |
| `TipoOperacion` | 51 | `cbc:InvoiceTypeCode/@listID` |
"""

from __future__ import annotations

from enum import Enum


class TipoComprobante(str, Enum):
    """Catálogo 01 — tipo de comprobante que emite el sistema."""

    FACTURA = "01"
    BOLETA = "03"
    NOTA_CREDITO = "07"
    NOTA_DEBITO = "08"

    @property
    def raiz_ubl(self) -> str:
        """Elemento raíz del estándar para este tipo."""
        return {
            TipoComprobante.FACTURA: "Invoice",
            TipoComprobante.BOLETA: "Invoice",
            TipoComprobante.NOTA_CREDITO: "CreditNote",
            TipoComprobante.NOTA_DEBITO: "DebitNote",
        }[self]

    @property
    def es_nota(self) -> bool:
        return self in (TipoComprobante.NOTA_CREDITO, TipoComprobante.NOTA_DEBITO)


class Moneda(str, Enum):
    """Catálogo 02 — moneda del comprobante."""

    PEN = "PEN"
    USD = "USD"

    @property
    def nombre(self) -> str:
        return "SOLES" if self is Moneda.PEN else "DÓLARES AMERICANOS"


class UnidadMedida(str, Enum):
    """Catálogo 03 — unidad de medida (subconjunto operativo)."""

    UNIDAD = "NIU"
    KILOGRAMO = "KGM"
    CAJA = "BX"
    LITRO = "LTR"
    SERVICIO = "ZZ"
    BOLSA = "BG"
    SACO = "SA"


class Tributo(str, Enum):
    """Catálogo 05 — código de tributo y su código internacional."""

    IGV = "1000"
    ISC = "2000"
    ICBPER = "7152"
    EXPORTACION = "9995"
    EXONERADO = "9997"
    INAFECTO = "9998"

    @property
    def nombre(self) -> str:
        return {
            Tributo.IGV: "IGV",
            Tributo.ISC: "ISC",
            Tributo.ICBPER: "ICBPER",
            Tributo.EXPORTACION: "EXP",
            Tributo.EXONERADO: "EXO",
            Tributo.INAFECTO: "INA",
        }[self]

    @property
    def codigo_internacional(self) -> str:
        """Código UN/ECE 5153 que acompaña al tributo en el UBL."""
        return {
            Tributo.IGV: "VAT",
            Tributo.ISC: "EXC",
            Tributo.ICBPER: "OTH",
            Tributo.EXPORTACION: "FRE",
            Tributo.EXONERADO: "VAT",
            Tributo.INAFECTO: "FRE",
        }[self]

    @property
    def categoria(self) -> str:
        """Identificador de la categoría de impuesto (UN/ECE 5305)."""
        return {
            Tributo.IGV: "S",
            Tributo.ISC: "S",
            Tributo.ICBPER: "S",
            Tributo.EXPORTACION: "G",
            Tributo.EXONERADO: "E",
            Tributo.INAFECTO: "O",
        }[self]


class AfectacionIGV(str, Enum):
    """Catálogo 07 — tipo de afectación del IGV."""

    GRAVADO_ONEROSA = "10"
    GRAVADO_RETIRO_PREMIO = "11"
    EXONERADO_ONEROSA = "20"
    EXONERADO_TRANSFERENCIA = "21"
    INAFECTO_ONEROSA = "30"
    INAFECTO_RETIRO_BONIFICACION = "31"
    EXPORTACION = "40"

    @property
    def es_gravada(self) -> bool:
        return self.value in ("10", "11")

    @property
    def tributo(self) -> Tributo:
        if self.es_gravada:
            return Tributo.IGV
        if self.value in ("20", "21"):
            return Tributo.EXONERADO
        if self.value in ("30", "31"):
            return Tributo.INAFECTO
        return Tributo.EXPORTACION


class SistemaISC(str, Enum):
    """Catálogo 08 — sistema de cálculo del ISC.

    **No** identifica personas: decide cómo se calcula el impuesto de la línea.
    """

    AD_VALOR = "01"
    MONTO_FIJO = "02"
    PRECIO_VENTA_PUBLICO = "03"


class TipoDocumentoIdentidad(str, Enum):
    """Catálogo 06 — tipo de documento de identidad del receptor."""

    NO_DOMICILIADO = "0"
    DNI = "1"
    CARNET_EXTRANJERIA = "4"
    RUC = "6"
    PASAPORTE = "7"
    CEDULA_DIPLOMATICA = "A"


class TipoOperacion(str, Enum):
    """Catálogo 51 — tipo de operación (viaja en `InvoiceTypeCode/@listID`)."""

    VENTA_INTERNA = "0101"
    EXPORTACION = "0200"


class TipoFormaPago(str, Enum):
    """Forma de pago SUNAT (RS 193-2020)."""

    CONTADO = "Contado"
    CREDITO = "Credito"


class MotivoNotaCredito(str, Enum):
    """Catálogo 09 — subconjunto operativo."""

    ANULACION_OPERACION = "01"
    ANULACION_RUC = "02"
    CORRECCION_DESCRIPCION = "03"
    DESCUENTO_GLOBAL = "04"
    DESCUENTO_ITEM = "05"
    DEVOLUCION_TOTAL = "06"
    DEVOLUCION_ITEM = "07"
    BONIFICACION = "08"


class MotivoNotaDebito(str, Enum):
    """Catálogo 10 — subconjunto operativo."""

    INTERESES_MORA = "01"
    AUMENTO_VALOR = "02"
    PENALIDADES = "03"


class TipoDocumentoRelacionado(str, Enum):
    """Catálogo 12 — documento relacionado (el vale del legado viaja como "otros")."""

    OTROS = "99"
