# Catálogos SUNAT usados en el sistema

Cada catálogo se expone por la API (`GET /api/v1/catalogos/{codigo}`) y se referencia en la
[matriz de trazabilidad](../../../docs/arquitectura/04-matriz-trazabilidad-normativa.md).

> **Nota de alcance:** se listan los códigos que el sistema necesita para facturas, boletas y notas.
> Los catálogos completos se cargan desde el maestro oficial de SUNAT; esta tabla es el contrato
> mínimo que el dominio debe conocer.

---

## Catálogo 01 — Tipo de documento (comprobante)

| Código | Descripción | ¿Lo emite el sistema? |
|---|---|---|
| `01` | Factura | Sí |
| `03` | Boleta de venta | Sí |
| `07` | Nota de crédito | Sí |
| `08` | Nota de débito | Sí |
| `09` | Guía de remisión remitente | No (fuera de alcance) |
| `12` | Ticket de máquina registradora | No |
| `20` | Comprobante de retención | No |
| `40` | Comprobante de percepción | No |

## Catálogo 02 — Moneda

| Código | Descripción |
|---|---|
| `PEN` | Sol |
| `USD` | Dólar estadounidense |

## Catálogo 03 — Unidad de medida (subconjunto operativo)

| Código | Descripción |
|---|---|
| `NIU` | Unidad (bienes) |
| `KGM` | Kilogramo |
| `BX` | Caja |
| `LTR` | Litro |
| `ZZ` | Servicio |

## Catálogo 05 — Tipo de tributo

| Código | Descripción | Código internacional | Uso |
|---|---|---|---|
| `1000` | IGV — Impuesto General a las Ventas | `VAT` | tasa 18% (ventas gravadas) |
| `1016` | IVAP | `VAT` | fuera de alcance (4%) |
| `2000` | ISC — Impuesto Selectivo al Consumo | `EXC` | tasa por producto |
| `7152` | ICBPER — Impuesto a las bolsas plásticas | `OTH` | monto fijo S/ 0.50 por bolsa |
| `9995` | Exportación | `FRE` | operaciones de exportación (afectación 40) |
| `9996` | Gratuito | `FRE` | transferencias gratuitas (afectación 11/21/31) |
| `9997` | Exonerado | `VAT` | operaciones exoneradas (afectación 20) |
| `9998` | Inafecto | `FRE` | operaciones inafectas (afectación 30) |
| `9999` | Otros tributos | `OTH` | tributos no clasificados |

## Catálogo 07 — Tipo de afectación del IGV

| Código | Descripción | ¿Genera IGV? |
|---|---|---|
| `10` | Gravado — operación onerosa | Sí (18%) |
| `11` | Gravado — retiro por premio | Sí |
| `12` | Gravado — retiro por donación | Sí |
| `13` | Gravado — retiro | Sí |
| `14` | Gravado — retiro por publicidad | Sí |
| `15` | Gravado — bonificaciones | Sí |
| `16` | Gravado — retiro por entrega a trabajadores | Sí |
| `17` | Gravado — IVAP | Sí |
| `20` | Exonerado — operación onerosa | No |
| `21` | Exonerado — transferencia gratuita | No |
| `30` | Inafecto — operación onerosa | No |
| `31` | Inafecto — retiro por bonificación | No |
| `32` | Inafecto — retiro | No |
| `33` | Inafecto — retiro por muestras médicas | No |
| `34` | Inafecto — retiro por convenio colectivo | No |
| `35` | Inafecto — retiro por premio | No |
| `36` | Inafecto — retiro por publicidad | No |
| `37` | Inafecto — retiro por entrega a trabajadores | No |
| `40` | Exportación de bienes o servicios | No (tasa 0%) |

## Catálogo 06 — Tipo de documento de identidad

Se usa para identificar al receptor (`cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID/@schemeID`)
y al emisor cuando corresponde.

> **Numeración:** el tipo de documento de identidad es el **catálogo 06**. El **08** es el de
> *sistema de cálculo del ISC* (ver más abajo), que es el que el enunciado señala como punto clave.

> **Subconjunto operativo soportado por el contrato:** `0`, `1`, `4`, `6`, `7`, `A`. Los códigos
> `B`–`G` existen en el catálogo SUNAT y se listan como referencia, pero el DTO de emisión los
> rechaza hasta que el negocio los requiera (misma convención que el catálogo 03).

| Código | Descripción | Validación en el sistema |
|---|---|---|
| `0` | Doc. tributario no domiciliado sin RUC | solo boleta a consumidor final |
| `1` | DNI | exactamente 8 dígitos numéricos |
| `4` | Carnet de extranjería | 9–12 alfanumérico |
| `6` | RUC | 11 dígitos + dígito verificador (RN-01) |
| `7` | Pasaporte | 8–12 alfanumérico |
| `A` | Cédula diplomática de identidad | 8–12 alfanumérico |
| `B` | Doc. de identidad del país de residencia | 8–15 alfanumérico |
| `C` | Tax Identification Number | 8–15 alfanumérico |
| `D` | Identification Number | 8–15 alfanumérico |
| `E` | TAM-UN | 8–15 alfanumérico |
| `F` | TAM-AN | 8–15 alfanumérico |
| `G` | TAM-SC | 8–15 alfanumérico |

### Reglas de combinación (RN-02)

| Comprobante | Documentos permitidos |
|---|---|
| Factura (`01`) | solo `6` (RUC) |
| Boleta (`03`) | `1`, `6`, `0` (consumidor final) |
| Nota de crédito/débito | el mismo del comprobante que modifica |

## Catálogo 08 — Sistema de cálculo del ISC ★

**Es el catálogo que el enunciado destaca.** No identifica personas: decide **cómo se calcula el ISC**
de cada línea. Sin él, el ISC solo puede calcularse de una forma (ad valorem) y las otras dos quedan
fuera del sistema.

| Código | Sistema | Fórmula del ISC de la línea | Datos que exige |
|:--:|---|---|---|
| `01` | **Ad valorem** | `isc = valor_venta × (tasa_isc / 100)` | `tasa_isc` |
| `02` | **Específico** | `isc = monto_fijo_isc × cantidad` | `monto_fijo_isc` (S/ por unidad de medida) |
| `03` | **Al valor** (precio de venta al público) | `isc = (precio_venta_publico − valor_venta_sin_isc) × cantidad` | `precio_venta_publico` |

Reglas del catálogo en el dominio (RN-06):

1. Si el producto **no** está afecto al ISC, `sistema_isc` es nulo y `isc = 0`.
2. Si está afecto, `sistema_isc` es **obligatorio** y solo se admite `01`, `02` o `03`.
3. Cada sistema exige **su** dato: `01` → `tasa_isc > 0`; `02` → `monto_fijo_isc > 0`; `03` →
   `precio_venta_publico > valor_venta_sin_isc`. Si falta, es error de negocio (422).
4. El ISC calculado **integra la base del IGV** (RN-05) y se declara en el XML con
   `cac:TaxScheme/cbc:ID = 2000`.

**Dónde viaja en el UBL:** el sistema/tasa se declara en
`cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TierRange` (con `cac:TaxScheme/cbc:ID`
= `2000`, `cbc:Name` = `ISC` y `cbc:TaxTypeCode` = `EXC`); el importe, en el `cbc:TaxAmount` del
mismo `cac:TaxSubtotal`.

## Catálogo 09 — Tipo de nota de crédito

| Código | Descripción |
|---|---|
| `01` | Anulación de la operación |
| `02` | Anulación por error en el RUC |
| `03` | Corrección por error en la descripción |
| `04` | Descuento global |
| `05` | Descuento por ítem |
| `06` | Devolución total |
| `07` | Devolución por ítem |
| `08` | Bonificación |
| `09` | Disminución en el valor |
| `10` | Otros conceptos |
| `11` | Ajustes de operaciones de exportación |
| `12` | Ajustes afectos al IVAP |

## Catálogo 10 — Tipo de nota de débito

| Código | Descripción |
|---|---|
| `01` | Intereses por mora |
| `02` | Aumento en el valor |
| `03` | Penalidades / otros conceptos |
| `11` | Ajustes de operaciones de exportación |
| `12` | Ajustes afectos al IVAP |

## Catálogo 51 — Tipo de operación

| Código | Descripción |
|---|---|
| `0101` | Venta interna (valor por defecto del sistema) |

> El catálogo 51 completo (exportación, venta interna a no domiciliados, operaciones sujetas a
> detracción, etc.) se carga desde el maestro; el dominio solo exige el formato de 4 dígitos y
> valida que exista en el catálogo cargado.

---

## Correspondencia catálogo → UBL

| Catálogo | Elemento UBL donde se usa |
|---|---|
| 01 | `cbc:InvoiceTypeCode` / `cbc:CreditNoteTypeCode` |
| 02 | `cbc:DocumentCurrencyCode` |
| 03 | `cbc:InvoicedQuantity/@unitCode` |
| 05 | `cac:TaxScheme/cbc:ID` |
| 06 | `cac:PartyIdentification/cbc:ID/@schemeID` (emisor y receptor) |
| 07 | `cbc:TaxExemptionReasonCode` |
| **08** | `cac:TaxCategory/cbc:TierRange` (con `cac:TaxScheme/cbc:ID = 2000`) |
| 09 | `cac:DiscrepancyResponse/cbc:ResponseCode` (NC) |
| 10 | `cac:DiscrepancyResponse/cbc:ResponseCode` (ND) |
| 51 | `cbc:InvoiceTypeCode/@listID` |
