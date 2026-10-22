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

## Catálogo 08 — Sistema de cálculo del ISC · y catálogo 06 — Tipo de documento de identidad ★

> **Aclaración de numeración.** En la numeración oficial del SEE, el **catálogo 06** es el de *tipo de
> documento de identidad* y el **catálogo 08** es el de *sistema de cálculo del ISC*. El enunciado del
> examen señala "el catálogo 8" como punto clave; para no depender de esa numeración se documentan
> **ambos**: los sistemas de ISC (`01` ad valorem, `02` específico, `03` al valor) y los tipos de
> documento de identidad.

| Sistema de cálculo del ISC (catálogo 08) | Descripción |
|---|---|
| `01` | Ad valorem (porcentaje sobre el valor) |
| `02` | Específico (monto por unidad) |
| `03` | Al valor (sobre el precio de venta) |

### Tipo de documento de identidad (catálogo 06)

**Es el catálogo que el examen señala como punto clave.** Se usa para identificar al receptor
(`cac:AccountingCustomerParty`) y al emisor cuando corresponde.

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
| 07 | `cbc:TaxExemptionReasonCode` |
| **08** | `cbc:ID/@schemeID` (emisor y receptor) |
| 09 | `cac:DiscrepancyResponse/cbc:ResponseCode` (NC) |
| 10 | `cac:DiscrepancyResponse/cbc:ResponseCode` (ND) |
| 51 | `cbc:InvoiceTypeCode/@listID` |
