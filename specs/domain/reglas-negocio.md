# Reglas de Negocio — Motor de facturación electrónica

Cada regla tiene ID, origen normativo y el artefacto donde se aplica. La numeración **RN-xx** es la
que se referencia en la matriz de trazabilidad (`docs/arquitectura/04-matriz-trazabilidad-normativa.md`).

---

## A. Identificación y validación de documentos

### RN-01 — Validación de RUC (dígito verificador)

Un RUC tiene 11 dígitos numéricos y debe cumplir el algoritmo módulo 11:

```text
factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
suma     = Σ (digito_i × factor_i) para los 10 primeros dígitos
resto    = suma mod 11
digito   = 11 − resto
si digito == 10 → digito = 0
si digito == 11 → digito = 1
válido   = (digito == digito_verificador)  # el dígito 11
```

Prefijos válidos: `10` (persona natural), `15`, `17`, `20` (persona jurídica).
**Origen:** SUNAT — validación de RUC. **Aplica en:** `Empresa.ruc`, `Cliente` tipo 6.

### RN-02 — Documentos de identidad del receptor (catálogo 8)

| Código | Documento | Validación |
|---|---|---|
| `0` | Doc. tributario no domiciliado sin RUC | solo para boletas a consumidor final |
| `1` | DNI | exactamente 8 dígitos numéricos |
| `4` | Carnet de extranjería | 9–12 alfanumérico |
| `6` | RUC | RN-01 |
| `7` | Pasaporte | 8–12 alfanumérico |
| `A` | Cédula diplomática | 8–12 alfanumérico |

Reglas de combinación:

- **Factura (01)** → el receptor **debe** tener RUC (`6`).
- **Boleta (03)** → DNI (`1`), RUC (`6`) o consumidor final (`0` con número `0`). Sobre **S/ 700**
  el Reglamento de Comprobantes de Pago exige identificar al comprador: con consumidor final solo
  hasta ese monto (umbral configurable, verificar el texto vigente).
- **NC/ND (07/08)** → heredan el receptor del comprobante que modifican.

**Origen:** **Catálogo 8** (punto clave señalado en el caso). **Aplica en:** `Cliente.tipo_documento`.

### RN-03 — Integridad del receptor

`razon_social` obligatoria (mínimo 3 caracteres). Si el documento es RUC, `ubigeo` y `direccion` son
obligatorios para el XML (ruta UBL `cac:AccountingCustomerParty`).

---

## B. Cálculo de impuestos

### RN-04 — Valor unitario sin IGV

```text
Si afectación ∈ {10,11,12,13,14,15,16,17}   (gravado):
    valor_unitario = precio_unitario / (1 + tasa_igv/100)
    con tasa_igv = 18.00 → valor_unitario = precio_unitario / 1.18
Si afectación ∈ {20,21,30..37,40}:
    valor_unitario = precio_unitario        (no se desagrega IGV)
```

`precio_unitario` es el precio de venta al público (**con** IGV). `valor_unitario` es la base imponible
(**sin** IGV). Ambos se reportan en el XML.

### RN-05 — IGV por línea

```text
base_linea = valor_unitario × cantidad − descuento
base_igv   = base_linea + isc_linea
si afectación es gravada (10, 11):
    igv_linea = base_igv × (tasa_igv/100)
si exonerado (20–21), inafecto (30–37) o exportación (40):
    igv_linea = 0
```

> El **descuento reduce la base imponible** antes de calcular el IGV. Calcular el impuesto sobre el
> valor bruto y descontar después sobrestima el tributo.

### RN-06 — ISC por línea

```text
isc_linea = valor_unitario × cantidad × (tasa_isc/100)
```

`tasa_isc` = 0 cuando el producto no está afecto. El **ISC forma parte de la base imponible del
IGV**: la base es el valor de venta incluido el ISC (TUO de la Ley del IGV). Fórmulas:

```text
base_igv = base_linea + isc_linea
igv_linea = base_igv × (tasa_igv/100)
```

### RN-07 — ICBPER por línea

Es un **monto fijo por bolsa**, no un porcentaje:

```text
icbper_linea = 0.50 × cantidad_de_bolsas
```

La tasa vigente desde 2023 es **S/ 0.50** por bolsa plástica. Solo aplica si
`Producto.es_bolsa_plastica = true`.

### RN-08 — Redondeo

- Se redondea **half-up a 2 decimales por línea**.
- Los totales son la **suma de líneas ya redondeadas** (nunca se recalcula desde los unitarios).
- Si la diferencia entre el total calculado y el total sumado supera `0.01`, se ajusta la **última
  línea** y se registra la observación.

### RN-09 — Totales (nunca se reciben del cliente)

```text
op_gravada      = Σ (valor_unitario × cantidad − descuento) de líneas 10..17
op_exonerada    = Σ (...) de líneas 20..21
op_inafecta     = Σ (...) de líneas 30..37
op_exportacion  = Σ (...) de líneas 40
total_igv       = Σ igv_linea
total_isc       = Σ isc_linea
total_icbper    = Σ icbper_linea
importe_total   = op_gravada + op_exonerada + op_inafecta + op_exportacion
                  + total_igv + total_isc + total_icbper
```

El DTO de entrada **no acepta** el campo `totales`: si llega, se ignora y se recalcula
(protección contra manipulación).

---

## C. Numeración

### RN-10 — Serie según tipo de comprobante

| Tipo | Descripción | Serie |
|---|---|---|
| `01` | Factura | `F` + 3 dígitos (ej. `F001`) |
| `03` | Boleta | `B` + 3 dígitos (ej. `B001`) |
| `07` | Nota de crédito | hereda `F` o `B` del documento que modifica |
| `08` | Nota de débito | hereda `F` o `B` del documento que modifica |

**Formato de la serie (validación de emisión):**

```text
^[FB][0-9]{3}$       4 caracteres: una letra del tipo + tres dígitos (001..999)
                     la letra debe corresponder al tipo de comprobante
                     la serie debe existir entre las series registradas por la empresa
```

### RN-11 — Correlativo

- Entero positivo, incremental, **sin huecos** por `tipo + serie`.
- Formato del número: `SERIE-CORRELATIVO` con correlativo de 8 dígitos (`F001-00000123`).
- La asignación es **atómica**: si la emisión falla, el correlativo se libera (no se consume).

### RN-12 — Unicidad

`(tipo, serie, correlativo)` es único. Un intento de duplicado es error de negocio (`409`), no de
esquema.

---

## D. Emisión y ciclo de vida

### RN-13 — Fecha de emisión

No puede ser **posterior a la fecha actual**. La hora se registra en formato `HH:mm:ss`.

### RN-14 — Detalle obligatorio

Un comprobante tiene **al menos una línea**. `cantidad > 0`. `descuento ≥ 0` y nunca mayor que el
valor de la línea.

### RN-15 — Inmutabilidad

Un comprobante en estado `EMITIDO`, `ACEPTADO` o `BAJA` **no se modifica**. Cualquier corrección se
hace con nota de crédito (total o parcial).

### RN-16 — Notas de crédito y débito

- `tipo ∈ {07, 08}`.
- `comprobante_referencia` obligatorio y debe existir en estado `ACEPTADO`.
- Motivo: **catálogo 09** (NC) o **catálogo 10** (ND).
- Una NC no puede superar el importe del comprobante original menos las NC previas.

### RN-17 — Estados

```text
BORRADOR → (emitir) → EMITIDO → (CDR 0) → ACEPTADO
                            └──→ (CDR ≠ 0) → RECHAZADO → (nuevo intento) → EMITIDO
ACEPTADO → (baja, plazo normativo) → BAJA
```

---

## E. Integración SUNAT

### RN-18 — Validación antes del envío

El XML se genera, se **firma digitalmente** y se **valida contra el XSD** antes de enviarse a la OSE.
Si no valida, no se envía y el comprobante queda `RECHAZADO` con el detalle del error.

### RN-19 — Procesamiento del CDR

| Código CDR | Significado | Acción |
|---|---|---|
| `0` | Aceptado sin observaciones | `estado = ACEPTADO` |
| `2000`–`3999` | **Rechazo**: el comprobante no es válido | `estado = RECHAZADO`, corregir y reemitir |
| `4000`+ | **Observación**: el comprobante es válido y fue aceptado | `estado = ACEPTADO` con observaciones; **nunca reemitir** |

> Confundir una observación con un rechazo lleva a reemitir un comprobante ya aceptado: duplicado
> tributario y correlativo perdido.

El CDR se guarda junto al XML (evidencia y trazabilidad).

### RN-20 — Reintentos

Ante error de comunicación (timeout, 5xx), se reintenta con **backoff exponencial** hasta 3 veces y
luego queda en cola `PENDIENTE_ENVIO`. Nunca se reemite un comprobante por un fallo de red.

---

## F. Migración del legado

### RN-21 — Semántica de la ficha

| Campo legado | Interpretación | Destino |
|---|---|---|
| `fecha` | fecha del movimiento | `MovimientoAlmacen.fecha` |
| `ingreso` | si tiene valor → entrada | `MovimientoAlmacen.tipo = INGRESO` |
| `salida` | si tiene valor → salida | `MovimientoAlmacen.tipo = SALIDA` |
| `producto` | texto libre | `Producto` (match por código/nombre normalizado) |
| `nro_documento` | documento informal | `FichaLegada.nro_documento` (se conserva) |

### RN-22 — Prohibición de pérdida

**Toda** ficha se migra o se marca `OBSERVADA` con motivo. Nunca se descarta en silencio. La ficha
conserva `id_ficha` y `origen_archivo` para auditoría (REQ-01).

### RN-23 — Documento informal

El `nro_documento` legado **no se convierte** en número de comprobante: se guarda como referencia
externa. Los comprobantes nuevos reciben correlativo propio (RN-11).

### RN-24 — Fechas inválidas

Fichas con fecha futura o sin fecha → `OBSERVADA`. No se inventan datos.

---

## Resumen de reglas

| Grupo | Reglas | Cantidad |
|---|---|---|
| Identificación | RN-01 a RN-03 | 3 |
| Impuestos | RN-04 a RN-09 | 6 |
| Numeración | RN-10 a RN-12 | 3 |
| Emisión | RN-13 a RN-17 | 5 |
| SUNAT | RN-18 a RN-20 | 3 |
| Migración | RN-21 a RN-24 | 4 |
| **Total** | | **24** |
