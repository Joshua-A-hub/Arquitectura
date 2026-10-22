# Tabla de match — campo SUNAT ↔ elemento UBL ↔ campo del DTO

**Origen:** indicación del docente: *"en SUNAT el identificador se llama `serie_numero`"* y *"esa
relación [es] una tabla de match"*.

Esta es la tabla de equivalencias **campo a campo**. Es la vista "de diccionario" de la
[trazabilidad normativa](04-matriz-trazabilidad-normativa.md): aquí el nombre del campo es el que usa
la normativa SUNAT, no un nombre inventado por el sistema.

---

## 1. Regla de nomenclatura: `serie_numero`

En SUNAT, el identificador del comprobante **no se llama "número"**: se llama **`serie_numero`** y se
compone de dos datos.

```text
serie_numero = serie + "-" + correlativo
ejemplo      = F001-00000123
               └┬─┘ └──┬───┘
              serie   correlativo (8 dígitos)
```

| Concepto | Nombre SUNAT | Regla | Ejemplo |
|---|---|---|---|
| Identificador completo | **`serie_numero`** | `^[FB][0-9]{3}-[0-9]{8}$` | `F001-00000123` |
| Prefijo | `serie` | 4 caracteres: letra del tipo + 3 dígitos | `F001` |
| Secuencia | `correlativo` | entero, sin huecos, por `tipo+serie` | `123` |

Consecuencia en el contrato: el campo se llama **`serie_numero`** (no `numero`) y es **derivado**:
el cliente no lo envía, lo asigna el sistema (RN-11).

> **Nota de compatibilidad:** donde antes se leía `numero` en el DTO, ahora se lee `serie_numero`.
> El campo `numero_documento` (documento de identidad) y `numero_linea` se mantienen: son otros datos.

---

## 2. Tabla de match (encabezado del comprobante)

| # | Campo SUNAT | Definición | Elemento UBL (ruta) | Campo DTO / dominio | Tipo | Oblig. | Regla |
|---|---|---|---|---|---|---|---|
| 1 | `ruc_emisor` | RUC del contribuyente que emite | `cac:AccountingSupplierParty/…/cbc:ID` (`@schemeID=6`) | contexto (`Empresa.ruc`) | 11 díg. | Sí | RN-01 |
| 2 | `razon_social_emisor` | Nombre o razón social del emisor | `…/cac:PartyLegalEntity/cbc:RegistrationName` | `Empresa.razon_social` | string(200) | Sí | — |
| 3 | `nombre_comercial_emisor` | Nombre comercial | `…/cac:PartyName/cbc:Name` | `Empresa.nombre_comercial` | string(200) | No | — |
| 4 | `ubigeo_emisor` | Código de ubigeo del domicilio fiscal | `…/cac:RegistrationAddress/cbc:ID` | `Empresa.ubigeo` | 6 díg. | Sí | RN-03 |
| 5 | `direccion_emisor` | Dirección del domicilio fiscal | `…/cac:AddressLine/cbc:Line` | `Empresa.direccion` | string(200) | Sí | RN-03 |
| 6 | `tipo_documento_receptor` | Tipo de documento de identidad (**catálogo 8**) | `cac:AccountingCustomerParty/…/cbc:ID` (`@schemeID`) | `cliente.tipo_documento` | cat. 8 | Sí | RN-02 |
| 7 | `numero_documento_receptor` | DNI (8) o RUC (11) del receptor | `…/cbc:ID` | `cliente.numero_documento` | string(15) | Sí | RN-02 |
| 8 | `razon_social_receptor` | Nombre o razón social del receptor | `…/cac:PartyLegalEntity/cbc:RegistrationName` | `cliente.razon_social` | string(200) | Sí | RN-03 |
| 9 | `ubigeo_receptor` | Ubigeo del receptor | `…/cac:RegistrationAddress/cbc:ID` | `cliente.ubigeo` | 6 díg. | Cond. | RN-03 |
| 10 | `direccion_receptor` | Dirección del receptor | `…/cac:AddressLine/cbc:Line` | `cliente.direccion` | string(200) | Cond. | RN-03 |
| 11 | `tipo_comprobante` | Factura (01) o boleta (03) — **catálogo 1** | `cbc:InvoiceTypeCode` | `Comprobante.tipo` | cat. 1 | Sí | RN-10 |
| 12 | **`serie_numero`** | Identificador completo del comprobante | `cbc:ID` | `Comprobante.serie_numero` | `F001-00000123` | Sí | RN-11, RN-12 |
| 13 | `fecha_emision` | Fecha de emisión | `cbc:IssueDate` | `Comprobante.fecha_emision` | date | Sí | RN-13 |
| 14 | `hora_emision` | Hora de emisión | `cbc:IssueTime` | `Comprobante.hora_emision` | time | Sí | RN-13 |
| 15 | `tipo_moneda` | Moneda del comprobante — **catálogo 2** | `cbc:DocumentCurrencyCode` | `Comprobante.moneda` | PEN/USD | Sí | RN-09 |
| 16 | `tipo_operacion` | Tipo de operación — catálogo 51 | `cbc:InvoiceTypeCode/@listID` | `Comprobante.tipo_operacion` | cat. 51 | Sí | RN-10 |
| 17 | `forma_pago` | Contado o crédito | `cac:PaymentTerms/cbc:ID` | `Comprobante.forma_pago` | enum | Sí | RN-09 |
| 18 | `monto_en_letras` | Importe total en letras (leyenda) | `cbc:Note` | `Totales.monto_en_letras` | string | Sí | RN-09 |
| 19 | `cantidad_items` | Cantidad de líneas del comprobante | `cbc:LineCountNumeric` | `Comprobante.detalle` (tamaño) | integer | Sí | RN-14 |

## 3. Tabla de match (detalle y tributos)

| # | Campo SUNAT | Definición | Elemento UBL (ruta) | Campo DTO / dominio | Tipo | Oblig. | Regla |
|---|---|---|---|---|---|---|---|
| 20 | `numero_linea` | Orden de la línea | `cac:InvoiceLine/cbc:ID` | `detalle[].numero_linea` | integer | Sí | RN-14 |
| 21 | `codigo_producto` | Código interno del bien | `…/cac:Item/cac:SellersItemIdentification/cbc:ID` | `detalle[].producto_codigo` | string(30) | Cond. | — |
| 22 | `descripcion_item` | Descripción del bien o servicio | `…/cac:Item/cbc:Description` | `detalle[].descripcion` | string(200) | Sí | — |
| 23 | `unidad_medida` | Unidad de medida — **catálogo 3** | `…/cbc:InvoicedQuantity/@unitCode` | `detalle[].unidad_medida` | cat. 3 | Sí | — |
| 24 | `cantidad` | Cantidad del bien | `…/cbc:InvoicedQuantity` | `detalle[].cantidad` | decimal(12,3) | Sí | RN-14 |
| 25 | `valor_unitario` | Valor unitario **sin** IGV | `…/cac:Price/cbc:PriceAmount` | `detalle[].valor_unitario` | decimal(12,6) | Sí | RN-04 |
| 26 | `precio_unitario` | Precio unitario **con** IGV | `…/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount` | `detalle[].precio_unitario` | decimal(12,6) | Sí | RN-04 |
| 27 | `valor_venta_item` | Valor de venta de la línea | `…/cbc:LineExtensionAmount` | `detalle[].total_linea` (base) | decimal(12,2) | Sí | RN-09 |
| 28 | `descuento_item` | Descuento aplicado a la línea | `…/cac:AllowanceCharge/cbc:Amount` | `detalle[].descuento` | decimal(12,2) | No | RN-09 |
| 29 | `afectacion_igv` | Afectación al IGV — **catálogo 7** | `…/cac:TaxCategory/cbc:TaxExemptionReasonCode` | `detalle[].afectacion_igv` | cat. 7 | Sí | QA-16 |
| 30 | `porcentaje_igv` | Tasa del IGV aplicada | `…/cac:TaxCategory/cbc:Percent` | `detalle[].tasa_igv` | 18.00 | Sí | RN-05 |
| 31 | `monto_igv` | IGV de la línea | `…/cac:TaxSubtotal/cbc:TaxAmount` (TaxScheme `1000`) | `detalle[].igv_linea` | decimal(12,2) | Sí | RN-05 |
| 32 | `monto_isc` | ISC de la línea | `…/cac:TaxSubtotal/cbc:TaxAmount` (TaxScheme `2000`) | `detalle[].isc_linea` | decimal(12,2) | Cond. | RN-06 |
| 33 | `monto_icbper` | ICBPER de la línea (S/ 0.50 por bolsa) | `…/cac:TaxSubtotal/cbc:TaxAmount` (TaxScheme `7152`) | `detalle[].icbper_linea` | decimal(12,2) | Cond. | RN-07 |

## 4. Tabla de match (totales)

| # | Campo SUNAT | Definición | Elemento UBL (ruta) | Campo DTO / dominio | Tipo | Oblig. | Regla |
|---|---|---|---|---|---|---|---|
| 34 | `total_gravado` | Suma de operaciones gravadas | `cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount` | `Totales.op_gravada` | decimal(12,2) | Sí | RN-09 |
| 35 | `total_exonerado` | Suma de operaciones exoneradas | `…/cbc:TaxableAmount` (afect. 20) | `Totales.op_exonerada` | decimal(12,2) | Cond. | RN-09 |
| 36 | `total_inafecto` | Suma de operaciones inafectas | `…/cbc:TaxableAmount` (afect. 30) | `Totales.op_inafecta` | decimal(12,2) | Cond. | RN-09 |
| 37 | `total_exportacion` | Suma de exportación | `…/cbc:TaxableAmount` (afect. 40) | `Totales.op_exportacion` | decimal(12,2) | Cond. | RN-09 |
| 38 | `total_igv` | IGV total del comprobante | `cac:TaxTotal/cbc:TaxAmount` | `Totales.total_igv` | decimal(12,2) | Sí | RN-05 |
| 39 | `total_isc` | ISC total | `cac:TaxTotal/cbc:TaxAmount` (tax `2000`) | `Totales.total_isc` | decimal(12,2) | Cond. | RN-06 |
| 40 | `total_icbper` | ICBPER total | `cac:TaxTotal/cbc:TaxAmount` (tax `7152`) | `Totales.total_icbper` | decimal(12,2) | Cond. | RN-07 |
| 41 | `total_valor_venta` | Valor de venta (sin impuestos) | `cac:LegalMonetaryTotal/cbc:LineExtensionAmount` | `Totales` (suma) | decimal(12,2) | Sí | RN-09 |
| 42 | `total_precio_venta` | Valor de venta + IGV | `cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount` | `Totales` (calculado) | decimal(12,2) | Sí | RN-09 |
| 43 | `importe_total` | Importe total a pagar | `cac:LegalMonetaryTotal/cbc:PayableAmount` | `Totales.importe_total` | decimal(12,2) | Sí | RN-09 |

## 5. Tabla de match (notas)

| # | Campo SUNAT | Definición | Elemento UBL (ruta) | Campo DTO / dominio | Tipo | Oblig. | Regla |
|---|---|---|---|---|---|---|---|
| 44 | `tipo_nota` | Nota de crédito (07) o débito (08) | `cbc:CreditNoteTypeCode` / `cbc:DebitNoteTypeCode` | `Comprobante.tipo` (tipo 07/08) | cat. 1 | Sí | RN-16 |
| 45 | `motivo_nota` | Código de motivo | `cac:DiscrepancyResponse/cbc:ResponseCode` | `Comprobante.motivo_codigo` (tipo 07/08) | cat. 9/10 | Sí | RN-16 |
| 46 | `descripcion_motivo` | Texto del motivo | `cac:DiscrepancyResponse/cbc:Description` | `Comprobante.descripcion_motivo` (tipo 07/08) | string(200) | Sí | RN-16 |
| 47 | `doc_relacionado` | `serie_numero` del comprobante modificado | `cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID` | `Comprobante.comprobante_referencia` (tipo 07/08) | `F001-…` | Sí | RN-16 |

---

## 6. Cómo se lee esta tabla

1. Busca el campo por su **nombre SUNAT** (columna 2) — por ejemplo `serie_numero`.
2. La columna 4 te dice **exactamente** dónde va en el XML (ruta UBL).
3. La columna 5 te dice **cómo se llama en el sistema** (DTO o dominio).
4. La columna 8 te dice **qué regla lo valida** (RN-xx de `specs/domain/reglas-negocio.md`).

**Cobertura:** 47 campos mapeados · 10 con obligatoriedad condicional · 14 reglas distintas referenciadas.

> Esta tabla es la contraparte "de diccionario" de la matriz de trazabilidad: la matriz ordena por
> obligación normativa; esta ordena por **nombre de campo** para que un desarrollador encuentre rápido
> dónde poner cada dato.
