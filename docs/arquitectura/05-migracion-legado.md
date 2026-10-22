# Legado y Migración de Datos — fichas del almacén

**Requisito del caso:** *"**Legado y Migración de Datos**: toda la información histórica del software
básico de mercadería (fecha, ingreso, salida, producto, `nro_documento`) debe acoplarse y mapearse
limpiamente hacia las nuevas entidades del sistema sin perder trazabilidad."*

---

## 1. El problema

El sistema anterior no guardaba entidades: guardaba **fichas sueltas** con texto libre. No hay
claves, no hay catálogo de productos y el `nro_documento` es un número interno sin validez tributaria.
Migrar no es "pasar datos": es **reconstruir entidades** sin inventar información.

## 2. Estrategia: carril con trazabilidad

```text
 Ficha legada ──▶ Normalizar ──▶ ¿Coincide con el maestro? ──sí──▶ MIGRADA
                                       │
                                       └──no──▶ OBSERVADA (con motivo)
```

**Ninguna ficha se descarta en silencio** (RN-22). Toda ficha termina en `MIGRADA` u `OBSERVADA`, y
siempre conserva su identificador de origen.

## 3. Mapeo campo por campo

| Campo legado | Tipo | Transformación | Destino | Si falta o es inválido |
|---|---|---|---|---|
| `id_ficha` | texto | se conserva tal cual | `FichaLegada.id_ficha` | bloqueante: no se puede migrar |
| `fecha` | texto | parseo a `YYYY-MM-DD`; rechaza fechas futuras | `MovimientoAlmacen.fecha` | OBSERVADA: "fecha inválida o futura" |
| `ingreso` | texto | si tiene valor → movimiento de entrada | `MovimientoAlmacen.tipo = INGRESO` | ver regla de exclusividad |
| `salida` | texto | si tiene valor → movimiento de salida | `MovimientoAlmacen.tipo = SALIDA` | ver regla de exclusividad |
| `producto` | texto libre | normalizar (mayúsculas, sin tildes, trim) y buscar en el maestro | `MovimientoAlmacen.producto_codigo` | OBSERVADA: "producto no identificado" |
| `nro_documento` | texto | **se conserva, no se convierte** | `FichaLegada.nro_documento` | se migra igual: es referencia externa |
| `origen_archivo` | — | nombre del archivo/hoja de origen | `FichaLegada.origen_archivo` | se completa con "desconocido" |

### Regla de exclusividad ingreso/salida

- Si **ambos** tienen valor → `OBSERVADA` (no se puede inferir la intención).
- Si **ninguno** tiene valor → `OBSERVADA`.
- Exactamente uno → se determina el tipo.

## 4. Reconstrucción de entidades

| Entidad nueva | Cómo se reconstruye | Riesgo |
|---|---|---|
| `Producto` | match exacto por código; luego por nombre normalizado; si no, se crea en un catálogo **propuesto** y la ficha queda OBSERVADA | duplicados por variantes de nombre |
| `MovimientoAlmacen` | una ficha = un movimiento | fichas que en realidad eran una venta (varias líneas) |
| `Cliente` | **no se reconstruye**: el legado no tiene datos del cliente | dato perdido: aceptado y declarado |
| `Comprobante` | **no se reconstruye**: el `nro_documento` no es un comprobante válido | requiere refacturación manual |

> **Decisión clave:** el sistema **no inventa** comprobantes históricos. El legado sirve para
> reconstruir el **kardex** (movimientos), no para emitir comprobantes retroactivos.

## 5. Contrato del proceso

```text
POST /api/v1/migracion/fichas
{
  "fichas": [
    {"id_ficha":"F-0001","fecha":"2026-05-01","ingreso":"10 cajas","salida":null,
     "producto":"arroz 50 kg","nro_documento":"INT-8891","origen_archivo":"almacen_2026.xlsx"}
  ]
}
```

Respuesta:

```json
{
  "total": 1, "migradas": 1, "observadas": 0,
  "detalle": [{"id_ficha":"F-0001","estado":"MIGRADA","entidad_destino_id":"...","observacion":null}]
}
```

## 6. Criterios de aceptación

| ID | Criterio |
|---|---|
| MIG-01 | Toda ficha del lote aparece en el detalle de la respuesta |
| MIG-02 | `migradas + observadas = total` |
| MIG-03 | Una ficha observada siempre trae motivo legible |
| MIG-04 | El `nro_documento` original es consultable después de migrar |
| MIG-05 | Re-ejecutar el mismo lote no duplica movimientos (idempotencia por `id_ficha`) |
| MIG-06 | Las fechas futuras quedan observadas |

## 7. Idempotencia y reproceso

El proceso es **idempotente por `id_ficha`**: si la ficha ya fue migrada, no se duplica y se informa
`estado = MIGRADA` con el `entidad_destino_id` existente. Esto permite reprocesar el mismo archivo sin
generar basura, y es lo que hace auditable la migración.

## 8. Plan de ejecución sugerido

1. **Inventario**: contar fichas y clasificar por archivo de origen.
2. **Limpieza**: normalizar productos contra el maestro (proceso asistido, con reporte de no
   encontrados).
3. **Migración en seco** (*dry run*): reporte de qué se migraría y qué se observaría, sin escribir.
4. **Corrección** de las observadas con el área de almacén.
5. **Migración definitiva** por lotes, con respaldo y conteo de control.
