# Modelo de Dominio — Facturación Electrónica ABC Software Corp

**Entregable E1 (parte 1):** modelo de dominio y contratos de datos.
Ver también: [`reglas-negocio.md`](reglas-negocio.md), [`../contracts/`](../contracts/) y el
**diagrama de clases** en [`docs/arquitectura/07-diagrama-clases.md`](../../docs/arquitectura/07-diagrama-clases.md).

---

## 1. Lenguaje del dominio

| Término | Definición | Sinónimo del negocio |
|---|---|---|
| **Emisor** | Empresa que vende y emite el comprobante (ABC Software Corp) | "la empresa" |
| **Receptor** | Cliente que compra; puede ser persona natural o jurídica | "el cliente" |
| **Comprobante** | Documento electrónico con validez tributaria (factura, boleta, NC, ND) | "el documento" |
| **Línea de detalle** | Ítem vendido dentro del comprobante | "el producto de la venta" |
| **Tributo** | Impuesto aplicado sobre una base (IGV, ISC, ICBPER) | "el impuesto" |
| **Ficha legada** | Registro informal del software anterior | "el cuaderno" |
| **CDR** | Constancia de Recepción que devuelve SUNAT | "el cargo" |
| **OSE** | Operador de Servicios Electrónicos que transporta el XML a SUNAT | "el intermediario" |

## 2. Entidades

### 2.1 Empresa (emisor) — `Empresa`

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `ruc` | string(11) | sí | formato RUC + dígito verificador (RN-01) |
| `razon_social` | string(200) | sí | — |
| `nombre_comercial` | string(200) | no | — |
| `ubigeo` | string(6) | sí | catálogo de ubigeo |
| `direccion` | string(200) | sí | — |
| `regimen_tributario` | enum | sí | RMT, RER, REG, NRUS — **NRUS no puede emitir facturas** (solo boletas) |
| `certificado_digital_id` | string | sí (para emitir) | referencia al certificado, nunca la clave |

### 2.2 Cliente (receptor) — `Cliente`

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `id` | uuid | sí | interno |
| `tipo_documento` | string(1) | sí | **catálogo 8** (RN-02) |
| `numero_documento` | string(15) | sí | según tipo: RUC 11, DNI 8 (RN-02) |
| `razon_social` | string(200) | sí | para DNI: nombres y apellidos |
| `ubigeo` | string(6) | no | obligatorio cuando el documento lo exige |
| `direccion` | string(200) | no | — |
| `email` | string | no | para envío del comprobante |

### 2.3 Producto — `Producto`

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `codigo` | string(30) | sí | único |
| `descripcion` | string(200) | sí | — |
| `unidad_medida` | string(3) | sí | **catálogo 3** (NIU, KGM, BX, LTR, ZZ) |
| `precio_unitario` | decimal(12,2) | sí | **incluye IGV** (precio de venta) |
| `afectacion_igv` | string(2) | sí | **catálogo 7** (10, 20, 30, 40) |
| `tasa_isc` | decimal(5,2) | no | 0 si no aplica |
| `es_bolsa_plastica` | boolean | sí | dispara ICBPER (RN-07) |
| `stock_actual` | decimal(12,3) | sí | ≥ 0 |

### 2.4 Comprobante — `Comprobante` (raíz del agregado)

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `id` | uuid | sí | interno |
| `tipo` | string(2) | sí | **catálogo 1**: 01 factura, 03 boleta, 07 NC, 08 ND |
| `serie` | string(4) | sí | F### factura, B### boleta (RN-10) |
| `correlativo` | integer | sí | incremental por serie, sin huecos (RN-11) |
| `serie_numero` | string(13) | sí | `serie + "-" + correlativo` (ej. `F001-00000123`) — nomenclatura SUNAT |
| `fecha_emision` | date | sí | no futura (RN-13) |
| `hora_emision` | time | sí | — |
| `moneda` | string(3) | sí | **catálogo 2**: PEN, USD |
| `tipo_operacion` | string(4) | sí | catálogo 51 (por defecto `0101` venta interna) |
| `forma_pago` | enum | sí | `CONTADO` \| `CREDITO` |
| `cuotas` | Cuota[] | no | obligatorio si `CREDITO` |
| `cliente` | Cliente | sí | — |
| `detalle` | LineaDetalle[] | sí | ≥ 1 línea (RN-14) |
| `totales` | Totales | sí | calculados, nunca recibidos (RN-09) |
| `estado` | enum | sí | `BORRADOR`, `EMITIDO`, `ACEPTADO`, `RECHAZADO`, `PENDIENTE_ENVIO`, `BAJA` |
| `hash_xml` | string(64) | no | SHA-256 del XML |
| `xml` | binary | no | documento emitido (inmutable) |
| `cdr` | Cdr | no | respuesta de SUNAT/OSE |
| `comprobante_referencia` | string(13) | condicional | obligatorio en NC/ND (RN-16) |

### 2.5 Línea de detalle — `LineaDetalle`

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `numero_linea` | integer | sí | 1..n |
| `producto_codigo` | string(30) | sí | — |
| `descripcion` | string(200) | sí | — |
| `unidad_medida` | string(3) | sí | catálogo 3 |
| `cantidad` | decimal(12,3) | sí | > 0 |
| `valor_unitario` | decimal(12,6) | sí | **sin IGV** (calculado, RN-04) |
| `precio_unitario` | decimal(12,6) | sí | **con IGV** |
| `descuento` | decimal(12,2) | no | monto, no porcentaje |
| `afectacion_igv` | string(2) | sí | catálogo 7 |
| `tasa_igv` | decimal(5,2) | sí | 18.00 salvo exonerado/inafecto/exportación |
| `igv_linea` | decimal(12,2) | sí | calculado |
| `isc_linea` | decimal(12,2) | no | calculado |
| `icbper_linea` | decimal(12,2) | no | calculado |
| `total_linea` | decimal(12,2) | sí | calculado |

### 2.6 Totales — `Totales` (value object inmutable)

| Campo | Descripción |
|---|---|
| `op_gravada` | suma de líneas con afectación 10..17 |
| `op_exonerada` | suma con afectación 20..21 |
| `op_inafecta` | suma con afectación 30..37 |
| `op_exportacion` | suma con afectación 40 |
| `total_igv` | suma de IGV de las líneas gravadas |
| `total_isc` | suma de ISC |
| `total_icbper` | suma de ICBPER |
| `total_descuentos` | suma de descuentos |
| `importe_total` | operaciones + tributos (los descuentos ya están restados en cada operación) |
| `monto_en_letras` | leyenda obligatoria en el XML |

### 2.7 Ficha legada — `FichaLegada` (migración)

| Campo | Tipo | Origen |
|---|---|---|
| `id_ficha` | string | identificador de la ficha original |
| `fecha` | date | campo "fecha" |
| `tipo` | enum | derivado de si "ingreso" o "salida" tiene valor |
| `producto` | string | campo "producto" (texto libre) |
| `cantidad` | decimal | derivado del registro |
| `nro_documento` | string | campo "nro_documento" (informal) |
| `origen_archivo` | string | archivo/hoja de donde provino |
| `estado_migracion` | enum | `PENDIENTE`, `MIGRADA`, `OBSERVADA` |
| `entidad_destino_id` | uuid | a qué entidad nueva se mapeó |
| `observacion` | string | motivo si quedó observada |

## 3. Relaciones

```text
Empresa 1 ──── N Comprobante        (emisor)
Cliente 1 ──── N Comprobante        (receptor)
Comprobante 1 ──── N LineaDetalle   (agregado: el detalle no existe sin el comprobante)
LineaDetalle N ──── 1 Producto      (referencia por código, no por identidad)
Producto 1 ──── N MovimientoAlmacen (kardex: ingresos y salidas)
FichaLegada 1 ──── 0..1 MovimientoAlmacen / Comprobante   (trazabilidad de migración)
Comprobante 1 ──── 0..1 Comprobante (referencia de NC/ND)
```

**Agregados (DDD):**

- `Comprobante` es la **raíz de agregado**: protege sus líneas y sus totales. No se modifica una
  línea de un comprobante emitido; se emite una nota.
- `Producto` es agregado propio (stock).
- `FichaLegada` es un agregado de **migración**: se procesa en lote y deja rastro.

## 4. Invariantes del dominio

| ID | Invariante | Se hace cumplir en |
|---|---|---|
| **INV-01** | Un comprobante emitido es **inmutable** | servicio de emisión + estado |
| **INV-02** | `total_linea = (valor_unitario × cantidad − descuento) + igv + isc + icbper` | cálculo |
| **INV-03** | `importe_total = op_gravada + op_exonerada + op_inafecta + op_exportacion + total_igv + total_isc + total_icbper` | cálculo |
| **INV-04** | La numeración es única por `tipo + serie` | repositorio (transacción) |
| **INV-05** | Un comprobante no se emite si el cliente no tiene documento válido según catálogo 8 | validación |
| **INV-06** | Una NC/ND siempre referencia un comprobante existente y aceptado | validación |
| **INV-07** | Un comprobante no se emite si el RUC del emisor no valida | validación |
| **INV-08** | Toda ficha migrada conserva su `id_ficha` y su `origen_archivo` | migración |

## 5. Máquina de estados del comprobante

```text
BORRADOR ──emitir──▶ EMITIDO ──ACEPTADO(cdr 0)──▶ ACEPTADO
                        │
                        ├──RECHAZADO(cdr ≠ 0)──▶ RECHAZADO
                        └──baja──▶ BAJA
```

- Solo desde `BORRADOR` se puede modificar.
- `ACEPTADO` es terminal (solo se corrige con NC/ND).
- `RECHAZADO` permite corregir y reintentar emitiendo de nuevo.

## 6. Contratos de datos (DTOs)

Los DTOs se especifican como **JSON Schema** en [`../contracts/dto/`](../contracts/dto/) y se exponen
en el contrato OpenAPI [`../contracts/facturacion-api.yaml`](../contracts/facturacion-api.yaml).

| DTO | Uso | Archivo |
|---|---|---|
| `ComprobanteCreate` | petición de emisión | `comprobante-create.schema.json` |
| `ComprobanteResponse` | respuesta de emisión/consulta | `comprobante-response.schema.json` |
| `LineaDetalle` | detalle embebido | dentro de `comprobante-create` |
| `ClienteDTO` | alta y consulta de cliente | `cliente.schema.json` |
| `ProductoDTO` | catálogo de productos | `producto.schema.json` |
| `NotaCreate` | nota de crédito/débito | `nota-create.schema.json` |
| `MigracionRequest/Response` | migración de fichas | `migracion.schema.json` |
| `ErrorValidacion` | error uniforme | `error.schema.json` |

### Regla de los DTOs

- **Los totales nunca viajan en la petición**: se calculan en el dominio (evita manipulación).
- **Los DTOs no son las entidades**: el DTO de entrada no tiene `id`, `estado`, `hash` ni `cdr`.
- **El detalle es obligatorio y no vacío**: mínimo una línea.
- **Fechas en ISO 8601**; importes con 2 decimales; cantidades hasta 3.
