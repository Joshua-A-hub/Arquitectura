# Anexo 2 del PLE — campos de los libros 14.1 y 12.1

Mapeo **campo del Anexo 2 → origen en el dominio** para los dos libros que el sistema debe emitir.
Complementa a [`09-libros-sunat.md`](09-libros-sunat.md) (que describe la estructura) y a los DTOs
[`registro-venta.schema.json`](../../specs/contracts/dto/registro-venta.schema.json) y
[`movimiento-almacen.schema.json`](../../specs/contracts/dto/movimiento-almacen.schema.json).

> **Alcance.** Este documento **no genera** el archivo TXT del PLE ni lo envía: define el mapeo de
> datos y las reglas para generarlo en la fase siguiente. El orden y los códigos exactos deben
> contrastarse con el **Anexo 2 vigente de SUNAT** al implementar el exportador; aquí se usan como
> referencia de diseño, no como reemplazo del documento oficial.

---

## 1. Libro 14.1 — Registro de Ventas e Ingresos

Origen: `RegistroVenta` (proyección del comprobante aceptado, INV-10).

| # | Campo del Anexo 2 (referencial) | Origen en el dominio | Regla / catálogo |
|:--:|---|---|---|
| 1 | Período | `fecha_emision` (`AAAA-MM`) | — |
| 2 | CUO (código único de operación) | `id` del registro | único por período |
| 3 | Número correlativo del registro | orden de `fecha_emision` + `serie_numero` | — |
| 4 | Fecha de emisión | `comprobante.fecha_emision` | RN-13 |
| 5 | Tipo de comprobante | `comprobante.tipo` | **catálogo 01** |
| 6 | Serie | `comprobante.serie` | RN-10 |
| 7 | Número (correlativo) | `comprobante.correlativo` | RN-11 |
| 8 | Tipo de documento del cliente | `cliente.tipo_documento` | **catálogo 06** |
| 9 | Número de documento del cliente | `cliente.numero_documento` | RN-02 |
| 10 | Razón social del cliente | `cliente.razon_social` | RN-03 |
| 11 | Valor de exportación | `totales.op_exportacion` | RN-09 |
| 12 | Base imponible gravada | `totales.op_gravada` (**sin ISC**, regla 3277) | RN-05, RN-09 |
| 13 | Base imponible exonerada | `totales.op_exonerada` | RN-05 |
| 14 | Base imponible inafecta | `totales.op_inafecta` | RN-05 |
| 15 | IGV | `totales.total_igv` | RN-05 |
| 16 | ISC | `totales.total_isc` | RN-06 (catálogo 08) |
| 17 | ICBPER | `totales.total_icbper` | RN-07 |
| 18 | Importe total | `totales.importe_total` | RN-09 |
| 19 | Moneda | `comprobante.moneda` | **catálogo 02** |
| 20 | Tipo de cambio | `tipo_cambio` | obligatorio si la moneda ≠ PEN |
| 21 | Estado | `estado` (`REGISTRADO` / `ANULADO`) | INV-10, RN-15 |

**Reglas de generación**

1. Solo entran comprobantes en estado **`ACEPTADO`** (o `BAJA` → `ANULADO`); nunca `RECHAZADO` ni
   `PENDIENTE_ENVIO`.
2. Una **nota de crédito** aceptada genera su propia línea con importe negativo en la base que
   corrige; una nota de débito, positiva.
3. La base gravada **no incluye el ISC** (regla SUNAT 3277); el ISC va en su propia columna.
4. El tipo de cambio es obligatorio para USD (y para cualquier moneda distinta de PEN).

---

## 2. Libro 12.1 — Inventario Permanente en Unidades Físicas

Origen: `MovimientoAlmacen` (INV-11). Una fila por movimiento.

| # | Campo del Anexo 2 (referencial) | Origen en el dominio | Regla / tabla |
|:--:|---|---|---|
| 1 | Período | `fecha` (`AAAA-MM`) | — |
| 2 | CUO | `id` del movimiento | único |
| 3 | Correlativo del registro | orden por `fecha` + `id` | — |
| 4 | Tipo de operación | `tipo_operacion` | **tabla 12** SUNAT |
| 5 | Tipo de existencia | `tipo_existencia` | **tabla 5** SUNAT |
| 6 | Código del establecimiento | `establecimiento` | 4 dígitos (`0000` = casa matriz) |
| 7 | Fecha del movimiento | `fecha` | — |
| 8 | Tipo de documento de soporte | `documento_soporte.tipo` | **tabla 10** SUNAT |
| 9 | Serie del documento | `documento_soporte.serie` | — |
| 10 | Número del documento | `documento_soporte.numero` | RN-23 |
| 11 | Código del producto | `producto_codigo` | maestro de productos |
| 12 | Unidad de medida | `unidad_medida` | **tabla 6** ↔ **catálogo 03** |
| 13 | Cantidad | `cantidad` | > 0 |
| 14 | Costo unitario | `costo_unitario` | obligatorio en ingresos |
| 15 | Saldo (cantidad) | `saldo_cantidad` | acumulado por producto y establecimiento |
| 16 | Saldo (valor) | `saldo_valor` | kardex valorizado |

**Reglas de generación**

1. El saldo se **arrastra**: cada fila depende del movimiento anterior del mismo producto y
   establecimiento (INV-11).
2. La unidad de medida debe existir en la tabla 6 y tener equivalencia con el catálogo 03.
3. Un movimiento migrado conserva `origen_ficha_id` aunque el documento de soporte sea informal
   (RN-23); el `nro_documento` del legado **no** se convierte en comprobante.
4. Ingreso → exige costo unitario; salida → el costo sale del saldo valorizado.

---

## 3. Qué falta para exportar el PLE (fase siguiente)

| Pieza | Estado |
|---|---|
| Modelo de datos (`RegistroVenta`, `MovimientoAlmacen`) | definido en [`modelo-dominio.md`](../../specs/domain/modelo-dominio.md) §2.8 y §2.9 |
| DTOs | `registro-venta.schema.json` y `movimiento-almacen.schema.json` |
| Endpoints | `GET /libros/14-1` y `POST/GET /movimientos-almacen` |
| **Exportador TXT del PLE** | **no implementado**: requiere el Anexo 2 vigente y validación de estructura |
| **Validación del TXT** | pendiente (el validador de SUNAT es externo) |

[`09-libros-sunat.md`](09-libros-sunat.md) describe la estructura de negocio; este documento la
mapea a campos. Ninguno de los dos sustituye al Anexo 2 oficial.
