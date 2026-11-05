# Libros SUNAT 12.1 y 14.1

Dos libros que el sistema debe poder generar y que **no son el comprobante**: salen del mismo dato,
pero tienen estructura propia.

| Libro | Nombre | De dónde sale | Quién lo usa |
|---|---|---|---|
| **12.1** | Registro de Inventario Permanente en **Unidades Físicas** | de los movimientos de almacén (`MovimientoAlmacen`) | almacén y contabilidad |
| **14.1** | Registro de **Ventas e Ingresos** | de los comprobantes **aceptados** | contabilidad y SUNAT |

> El proyecto anterior solo mencionaba un "kardex" de pasada. Sin estos dos libros, el sistema no
> cierra: el 12.1 justifica el stock y el 14.1 declaración el ingreso.

---

## 1. Libro 12.1 — Inventario permanente en unidades físicas

### 1.1 Estructura del registro

| Columna | Origen | Catálogo / tabla |
|---|---|---|
| Período | mes del movimiento | `AAAA-MM` |
| Código del establecimiento | `movimiento.establecimiento` | 4 dígitos (`0000` = casa matriz) |
| Tipo de existencia | `movimiento.tipo_existencia` | **Tabla 5** SUNAT |
| Tipo de operación | `movimiento.tipo_operacion` | **Tabla 12** SUNAT |
| Documento de soporte | `movimiento.documento_soporte` | **Tabla 10** SUNAT |
| Fecha del documento | `movimiento.documento_soporte.fecha` | ISO 8601 |
| Unidad de medida | `movimiento.unidad_medida` | **Tabla 6** SUNAT, con equivalencia al **catálogo 03** |
| Cantidad | `movimiento.cantidad` | decimal(12,3) |
| Costo unitario | `movimiento.costo_unitario` | decimal(12,6) |
| Saldo (cantidad) | `movimiento.saldo_cantidad` | decimal(12,3) |
| Saldo (valor) | `movimiento.saldo_valor` | decimal(12,2) |

### 1.2 Reglas de generación

1. **Cada movimiento es una fila.** No se recalcula el pasado: el saldo se arrastra del movimiento
   anterior del mismo producto y establecimiento.
2. **Ingreso** → exige `costo_unitario`; **salida** → el costo se toma del saldo valorizado.
3. La **unidad de medida** debe existir en la tabla 6 y tener equivalencia declarada con el
   catálogo 03 (ej. `NIU` ↔ `NIU`, `BX` ↔ `BX`, `KGM` ↔ `KGM`).
4. Un movimiento migrado **conserva** `origen_ficha_id`, aunque el documento de soporte sea informal
   (RN-23: el `nro_documento` legado no sustituye un comprobante).
5. Nunca hay filas sin saldo: si el saldo no se puede calcular, el movimiento se rechaza (422).

### 1.3 Ejemplo de fila

```json
{
  "fecha": "2026-10-22",
  "tipo_movimiento": "SALIDA",
  "establecimiento": "0000",
  "tipo_existencia": "01",
  "tipo_operacion": "02",
  "documento_soporte": { "tipo": "01", "serie_numero": "F001-00000123", "fecha": "2026-10-22" },
  "producto_codigo": "ARR-50KG",
  "unidad_medida": "NIU",
  "cantidad": 10,
  "saldo_cantidad": 110,
  "saldo_valor": "4114.96"
}
```

### 1.4 Dónde está en el sistema

- DTO: [`specs/contracts/dto/movimiento-almacen.schema.json`](../../specs/contracts/dto/movimiento-almacen.schema.json)
- Endpoint: `POST /api/v1/movimientos-almacen` y `GET /api/v1/movimientos-almacen?desde=&hasta=`
- Entidad de dominio: `MovimientoAlmacen` en [`specs/domain/modelo-dominio.md`](../../specs/domain/modelo-dominio.md) §2.8
- Invariante: **INV-11**

---

## 2. Libro 14.1 — Registro de ventas e ingresos

### 2.1 Estructura del registro

| Columna | Origen | Catálogo |
|---|---|---|
| Fecha de emisión | `comprobante.fecha_emision` | — |
| Tipo de comprobante | `comprobante.tipo` | Catálogo 01 |
| `serie_numero` | `comprobante.serie_numero` | — |
| Documento del cliente | `cliente.tipo_documento` + `numero_documento` | **Catálogo 06** |
| Razón social | `cliente.razon_social` | — |
| Base gravada | `totales.op_gravada` | — |
| Base exonerada | `totales.op_exonerada` | — |
| Base inafecta | `totales.op_inafecta` | — |
| Base exportación | `totales.op_exportacion` | — |
| IGV | `totales.total_igv` | — |
| ISC | `totales.total_isc` | — |
| ICBPER | `totales.total_icbper` | — |
| Importe total | `totales.importe_total` | — |
| Moneda y tipo de cambio | `comprobante.moneda` + `tipo_cambio` | Catálogo 02 |
| Estado | `REGISTRADO` \| `ANULADO` | — |

### 2.2 Reglas de generación

1. **Un comprobante aceptado genera exactamente un registro** (INV-10). El registro es una
   proyección: no se edita a mano.
2. Una **nota de crédito** aceptada genera su propio registro (tipo `07`) con importe negativo en la
   base que corrige.
3. Si el comprobante pasa a `BAJA`, el registro cambia a `ANULADO`.
4. Con moneda distinta de `PEN`, `tipo_cambio` es obligatorio.
5. No se registran comprobantes en estado `RECHAZADO` ni `PENDIENTE_ENVIO`.

### 2.3 Ejemplo de fila

```json
{
  "fecha_emision": "2026-10-22",
  "tipo_comprobante": "01",
  "serie_numero": "F001-00000123",
  "cliente_documento": { "tipo": "6", "numero": "20512345671" },
  "cliente_razon_social": "DISTRIBUIDORA SELVA SAC",
  "base_gravada": "389.83",
  "base_exonerada": "60.00",
  "igv": "70.17",
  "icbper": "10.00",
  "importe_total": "530.00",
  "moneda": "PEN",
  "estado": "REGISTRADO",
  "comprobante_id": "33333333-3333-3333-3333-333333333333"
}
```

### 2.4 Dónde está en el sistema

- DTO: [`specs/contracts/dto/registro-venta.schema.json`](../../specs/contracts/dto/registro-venta.schema.json)
- Endpoint: `GET /api/v1/libros/14-1?desde=&hasta=`
- Entidad de dominio: `RegistroVenta` en [`specs/domain/modelo-dominio.md`](../../specs/domain/modelo-dominio.md) §2.9
- Invariante: **INV-10**

---

## 3. Relación con la matriz de trazabilidad

| Fila de la matriz | Qué cubre |
|---|---|
| 60 | Establecimiento y tipo de existencia (tabla 5) |
| 61 | Unidad de medida (tabla 6 ↔ catálogo 03) |
| 62 | Documento de soporte (tabla 10) |
| 63 | Registro de ventas (formato 14.1) |

---

## 4. Errores que este documento evita

| Error típico | Consecuencia | Cómo se evita |
|---|---|---|
| Llamar "kardex" y no definir el 12.1 | no se puede declarar inventario | estructura de campo obligatorio |
| Registrar ventas desde el DTO de entrada | se duplica o se registra algo no emitido | solo comprobantes `ACEPTADO` (INV-10) |
| Mezclar unidad de compra con unidad de venta | saldos incoherentes | equivalencia tabla 6 ↔ catálogo 03 |
| Convertir el `nro_documento` informal en comprobante | inventario legal falso | RN-23: se conserva como referencia |
