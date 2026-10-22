# Entregable E4 — Matriz de Trazabilidad Normativa

**Requisito del examen:** *"Matriz de Trazabilidad Normativa con cruces entre datos SUNAT y datos UBL."*

Cada fila cruza el **dato exigido por SUNAT** con su **elemento UBL 2.1**, el **campo del contrato
(DTO)**, la **regla de negocio** que lo valida y el **caso de prueba** que lo verifica.

> **Vista por nombre de campo:** si buscas el equivalente campo a campo con el nombre que usa SUNAT
> (por ejemplo `serie_numero`), usa la [tabla de match](08-tabla-match-sunat-ubl.md).

- Rutas UBL relativas al documento raíz (`Invoice` o `CreditNote`).
- `cbc:` = CommonBasicComponents · `cac:` = CommonAggregateComponents · `ext:`/`ds:` = extensiones y firma.
- Cardinalidad: `1` obligatorio, `0..1` opcional, `1..n` repetible.

---

## A. Encabezado del comprobante

| N° | Dato SUNAT | Norma / Catálogo | Elemento UBL (ruta) | Card. | Campo DTO | Regla / validación | Prueba |
|---|---|---|---|---|---|---|---|
| 1 | Versión UBL | Perfil SUNAT 2.1 | `/cbc:UBLVersionID` | 1 | — (fijo) | valor `2.1` | QA-01 |
| 2 | CustomizationID | Perfil SUNAT | `/cbc:CustomizationID` | 1 | — (fijo) | valor del perfil (`2.0`) | QA-01 |
| 3 | **`serie_numero`** (identificador del comprobante) | Catálogo 1 + serie/correlativo | `/cbc:ID` = `SERIE-CORRELATIVO` | 1 | `serie_numero` (serie + correlativo asignado) | RN-10, RN-11, RN-12 | QA-02 |
| 4 | Tipo de comprobante | **Catálogo 1** (01, 03, 07, 08) | `/cbc:InvoiceTypeCode` | 1 | `tipo` | enum cerrado | QA-03 |
| 5 | Tipo de operación | **Catálogo 51** | `/cbc:InvoiceTypeCode/@listID` | 1 | `tipo_operacion` | patrón 4 dígitos, por defecto `0101` | QA-03 |
| 6 | Fecha de emisión | Norma de emisión | `/cbc:IssueDate` | 1 | `fecha_emision` | RN-13 (no futura) | QA-04 |
| 7 | Hora de emisión | Norma de emisión | `/cbc:IssueTime` | 1 | `hora_emision` | formato `HH:mm:ss` | QA-04 |
| 8 | Moneda | **Catálogo 2** (PEN, USD) | `/cbc:DocumentCurrencyCode` | 1 | `moneda` | enum | QA-05 |
| 9 | Cantidad de líneas | Control de consistencia | `/cbc:LineCountNumeric` | 1 | — (calculado) | igual al tamaño de `detalle` | QA-06 |
| 10 | Observaciones / leyenda | Norma de comprobantes | `/cbc:Note` | 0..n | `observaciones` | texto libre, 500 | QA-06 |
| 11 | Monto en letras | Leyenda obligatoria | `/cbc:Note` (código 1000) | 1 | — (generado) | generado desde `importe_total` | QA-06 |
| 12 | Forma de pago | Norma SUNAT | `/cac:PaymentTerms/cbc:ID` | 1 | `forma_pago` | enum CONTADO/CREDITO | QA-07 |
| 13 | Cuotas (si es crédito) | Norma SUNAT | `/cac:PaymentTerms/cbc:Amount` + `/cbc:PaymentDueDate` | 0..n | `cuotas[]` | pendiente de regla (fase 2) | QA-07 |

## B. Emisor

| N° | Dato SUNAT | Norma / Catálogo | Elemento UBL (ruta) | Card. | Campo DTO | Regla / validación | Prueba |
|---|---|---|---|---|---|---|---|
| 14 | RUC del emisor | RUC + **Catálogo 8** | `/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID` (`@schemeID=6`) | 1 | contexto (no en el DTO) | RN-01 (dígito verificador) | QA-08 |
| 15 | Razón social del emisor | Norma SUNAT | `.../cac:PartyLegalEntity/cbc:RegistrationName` | 1 | contexto | no vacío | QA-08 |
| 16 | Nombre comercial | Norma SUNAT | `.../cac:PartyName/cbc:Name` | 0..1 | contexto | opcional | QA-08 |
| 17 | Domicilio fiscal (ubigeo) | Norma SUNAT | `.../cac:PartyLegalEntity/cac:RegistrationAddress/cbc:ID` | 1 | contexto | 6 dígitos | QA-09 |
| 18 | Dirección del emisor | Norma SUNAT | `.../cac:RegistrationAddress/cac:AddressLine/cbc:Line` | 1 | contexto | no vacío | QA-09 |

## C. Receptor

| N° | Dato SUNAT | Norma / Catálogo | Elemento UBL (ruta) | Card. | Campo DTO | Regla / validación | Prueba |
|---|---|---|---|---|---|---|---|
| 19 | Tipo de documento del receptor | **Catálogo 8** | `/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID` (`@schemeID`) | 1 | `cliente.tipo_documento` | RN-02 | QA-10 |
| 20 | Número de documento | RUC / DNI | mismo `cbc:ID` | 1 | `cliente.numero_documento` | RN-02 (11 RUC / 8 DNI) | QA-10 |
| 21 | Nombre o razón social | Norma SUNAT | `.../cac:PartyLegalEntity/cbc:RegistrationName` | 1 | `cliente.razon_social` | mínimo 3 caracteres | QA-11 |
| 22 | Ubigeo del receptor | Norma SUNAT | `.../cac:RegistrationAddress/cbc:ID` | 0..1 | `cliente.ubigeo` | obligatorio si receptor es RUC | QA-11 |
| 23 | Dirección del receptor | Norma SUNAT | `.../cac:RegistrationAddress/cac:AddressLine/cbc:Line` | 0..1 | `cliente.direccion` | obligatorio si receptor es RUC | QA-11 |

## D. Líneas de detalle

| N° | Dato SUNAT | Norma / Catálogo | Elemento UBL (ruta) | Card. | Campo DTO | Regla / validación | Prueba |
|---|---|---|---|---|---|---|---|
| 24 | Número de línea | Consistencia | `/cac:InvoiceLine/cbc:ID` | 1..n | `detalle[].numero_linea` | entero ≥ 1, correlativo | QA-12 |
| 25 | Código del producto | Norma SUNAT | `/cac:InvoiceLine/cac:Item/cac:SellersItemIdentification/cbc:ID` | 0..1 | `detalle[].producto_codigo` | existe en catálogo de productos | QA-12 |
| 26 | Descripción | Norma SUNAT | `/cac:InvoiceLine/cac:Item/cbc:Description` | 1 | `detalle[].descripcion` | 3–200 caracteres | QA-12 |
| 27 | Unidad de medida | **Catálogo 3** | `/cac:InvoiceLine/cbc:InvoicedQuantity/@unitCode` | 1 | `detalle[].unidad_medida` | enum NIU/KGM/BX/LTR/ZZ | QA-13 |
| 28 | Cantidad | Norma SUNAT | `/cac:InvoiceLine/cbc:InvoicedQuantity` | 1 | `detalle[].cantidad` | > 0, 3 decimales | QA-13 |
| 29 | Valor unitario sin IGV | Norma SUNAT | `/cac:InvoiceLine/cac:Price/cbc:PriceAmount` | 1 | `detalle[].valor_unitario` (calculado) | RN-04 | QA-14 |
| 30 | Precio unitario con IGV | Norma SUNAT | `/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount` | 1 | `detalle[].precio_unitario` | igual al precio de venta | QA-14 |
| 31 | Valor de venta de la línea | Norma SUNAT | `/cac:InvoiceLine/cbc:LineExtensionAmount` | 1 | — (calculado) | RN-09 | QA-14 |
| 32 | Descuento por línea | Norma SUNAT | `/cac:InvoiceLine/cac:AllowanceCharge/cbc:Amount` | 0..1 | `detalle[].descuento` | ≥ 0 y ≤ valor de línea | QA-15 |

## E. Tributos por línea

| N° | Dato SUNAT | Norma / Catálogo | Elemento UBL (ruta) | Card. | Campo DTO | Regla / validación | Prueba |
|---|---|---|---|---|---|---|---|
| 33 | Código de tributo | **Catálogo 5** (1000 IGV, 2000 ISC, 7152 ICBPER) | `/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID` | 1..n | derivado de `afectacion_igv` y `tasa_isc` | catálogo cerrado | QA-16 |
| 34 | Afectación al IGV | **Catálogo 7** (10, 20, 30, 40…) | `.../cac:TaxCategory/cbc:TaxExemptionReasonCode` | 1 | `detalle[].afectacion_igv` | enum del catálogo | QA-16 |
| 35 | Tasa del IGV | Norma IGV (18%) | `.../cac:TaxCategory/cbc:Percent` | 1 | — (18 o 0) | 18 solo si afectación gravada | QA-17 |
| 36 | Base imponible | Norma SUNAT | `.../cac:TaxSubtotal/cbc:TaxableAmount` | 1 | — (calculado) | RN-05 | QA-17 |
| 37 | Monto del IGV | Norma SUNAT | `.../cac:TaxSubtotal/cbc:TaxAmount` | 1 | — (calculado) | RN-05, redondeo RN-08 | QA-17 |
| 38 | Monto del ISC | Norma ISC | `/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal` (TaxScheme `2000`) | 0..1 | `detalle[].tasa_isc` | RN-06 | QA-18 |
| 39 | Monto del ICBPER | Ley de bolsas plásticas | `.../cac:TaxSubtotal` (TaxScheme `7152`) | 0..1 | `producto.es_bolsa_plastica` | RN-07: S/ 0.50 × bolsa | QA-18 |

## F. Totales del comprobante

| N° | Dato SUNAT | Norma / Catálogo | Elemento UBL (ruta) | Card. | Campo DTO | Regla / validación | Prueba |
|---|---|---|---|---|---|---|---|
| 40 | Total IGV | Norma SUNAT | `/cac:TaxTotal/cbc:TaxAmount` | 1 | — (calculado) | suma de IGV de líneas | QA-19 |
| 41 | Total ISC | Norma SUNAT | `/cac:TaxTotal/cbc:TaxAmount` (tax `2000`) | 0..1 | — (calculado) | suma de ISC | QA-19 |
| 42 | Total ICBPER | Norma SUNAT | `/cac:TaxTotal/cbc:TaxAmount` (tax `7152`) | 0..1 | — (calculado) | suma de ICBPER | QA-19 |
| 43 | Total valor de venta | Norma SUNAT | `/cac:LegalMonetaryTotal/cbc:LineExtensionAmount` | 1 | — (calculado) | gravada + exonerada + inafecta + exportación | QA-19 |
| 44 | Total con impuestos | Norma SUNAT | `/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount` | 1 | — (calculado) | valor de venta + tributos | QA-19 |
| 45 | Importe total a pagar | Norma SUNAT | `/cac:LegalMonetaryTotal/cbc:PayableAmount` | 1 | — (calculado) | RN-09, redondeo RN-08 | QA-19 |

## G. Notas de crédito y débito

| N° | Dato SUNAT | Norma / Catálogo | Elemento UBL (ruta) | Card. | Campo DTO | Regla / validación | Prueba |
|---|---|---|---|---|---|---|---|
| 46 | Tipo de nota | Catálogo 1 (07, 08) | `/cbc:CreditNoteTypeCode` (o `/cbc:DebitNoteTypeCode`) | 1 | `tipo` | enum | QA-20 |
| 47 | Motivo / sustento | **Catálogo 9** (NC) / **Catálogo 10** (ND) | `/cac:DiscrepancyResponse/cbc:ResponseCode` | 1 | `motivo_codigo` | catálogo según tipo | QA-20 |
| 48 | Descripción del motivo | Norma SUNAT | `/cac:DiscrepancyResponse/cbc:Description` | 1 | `descripcion_motivo` | 3–200 caracteres | QA-20 |
| 49 | Comprobante que modifica | Norma SUNAT | `/cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID` | 1 | referencia al `id` del original | RN-16: existe y está ACEPTADO | QA-20 |
| 50 | Importe de la nota | Norma SUNAT | `/cac:LegalMonetaryTotal/cbc:PayableAmount` | 1 | — (calculado) | RN-16: no supera el saldo del original | QA-20 |

## H. Firma y envío

| N° | Dato SUNAT | Norma / Catálogo | Elemento UBL (ruta) | Card. | Campo DTO | Regla / validación | Prueba |
|---|---|---|---|---|---|---|---|
| 51 | Firma digital | Norma de firma XMLDSig | `/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature` | 1 | — | certificado del emisor vigente | QA-21 |
| 52 | Hash del XML | Integridad | atributo `Id` de la firma / registro interno | 1 | `hash_xml` | SHA-256 calculado tras firmar | QA-21 |
| 53 | CDR | Norma SEE | registro interno (no viaja en el XML) | 1 | `cdr` | RN-19: código `0` = aceptado | QA-22 |
| 54 | Estado del comprobante | Norma SUNAT | registro interno | 1 | `estado` | máquina de estados RN-17 | QA-22 |

## I. Migración del legado (trazabilidad de datos)

| N° | Dato del legado | Transformación | Destino | Regla | Prueba |
|---|---|---|---|---|---|
| 55 | `fecha` | parseo ISO | `MovimientoAlmacen.fecha` | RN-21, RN-24 | QA-23 |
| 56 | `ingreso` / `salida` | si `ingreso` tiene valor → INGRESO; si `salida` → SALIDA | `MovimientoAlmacen.tipo` | RN-21 | QA-23 |
| 57 | `producto` | normalización + match contra catálogo | `Producto.codigo` | RN-21 | QA-23 |
| 58 | `nro_documento` | **no se convierte** en número de comprobante | `FichaLegada.nro_documento` | RN-23 | QA-24 |
| 59 | (sin dato) | identificador de origen | `FichaLegada.id_ficha` + `origen_archivo` | RN-22 | QA-24 |

---

## Resumen de cobertura

| Bloque normativo | Filas | Cobertura |
|---|---|---|
| Encabezado | 13 | Catálogo 1, 2, 51 |
| Emisor | 5 | RUC + catálogo 8 |
| Receptor | 5 | **Catálogo 8** (punto clave del examen) |
| Detalle | 9 | Catálogo 3 |
| Tributos | 7 | Catálogos 5 y 7; IGV, ISC, ICBPER |
| Totales | 6 | IGV + redondeo |
| Notas | 5 | Catálogos 9 y 10 |
| Firma y envío | 4 | XMLDSig + CDR |
| Migración | 5 | Trazabilidad REQ-01 |
| **Total** | **59** | 9 catálogos + 24 reglas |

## Casos de prueba referenciados

| ID | Verifica |
|---|---|
| QA-01 | Versión y perfil UBL correctos |
| QA-02 | Número `SERIE-CORRELATIVO` bien formado |
| QA-03 | Tipo de comprobante y tipo de operación del catálogo |
| QA-04 | Fecha no futura y hora válida |
| QA-05 | Moneda del catálogo 2 |
| QA-06 | Conteo de líneas y leyendas |
| QA-07 | Forma de pago y cuotas coherentes |
| QA-08 | RUC del emisor con dígito verificador |
| QA-09 | Ubigeo y dirección del emisor |
| QA-10 | Documento del receptor según catálogo 8 |
| QA-11 | Razón social y domicilio del receptor |
| QA-12 | Integridad de la línea |
| QA-13 | Unidad de medida y cantidad |
| QA-14 | Precio con y sin IGV coherentes |
| QA-15 | Descuento no excede la línea |
| QA-16 | Código de tributo y afectación |
| QA-17 | Cálculo del IGV |
| QA-18 | Cálculo de ISC e ICBPER |
| QA-19 | Totales cuadran |
| QA-20 | Nota válida sobre comprobante aceptado |
| QA-21 | Firma y hash presentes |
| QA-22 | CDR y transición de estado |
| QA-23 | Migración de una ficha completa |
| QA-24 | Ficha sin datos suficientes queda OBSERVADA |
