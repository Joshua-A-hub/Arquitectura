# ADR-0006: Emisión síncrona con validación previa y envío asíncrono (outbox)

- **Estado:** Aceptada · **implementación pendiente** (la fase del Taller 2 termina en el XML)
- **Fecha:** 2026-11-05
- **Decisores:** Alvarado Ichpas Benny Joshua (arquitectura), área tributaria

## Contexto

SUNAT (o la OSE) puede tardar o no responder. La regla del caso es dura: **sin XML válido y firmado
no existe comprobante**, y un fallo de red **no puede reemitir** (RN-20). El diseño debía decidir
dónde se guarda el comprobante y en qué orden.

## Alternativas consideradas

| Opción | Qué implica | Veredicto |
|---|---|---|
| Enviar primero y guardar si todo sale bien | un timeout pierde un comprobante ya numerado | **Descartada** |
| Emisión totalmente síncrona | el usuario espera a SUNAT; un timeout deja el sistema sin saber si envió | Descartada |
| **Guardar el XML validado y enviar después (outbox)** | el estado `PENDIENTE_ENVIO` es persistente y un worker reintenta con backoff | **Elegida** |

## Decisión

1. Orden del flujo (RN-18): validar el DTO → validar reglas → calcular → **generar XML** →
   **validar contra el esquema oficial** → **firmar** → registrar en el outbox → responder.
2. El comprobante se persiste con su XML **antes** de intentar el envío, en estado
   `PENDIENTE_ENVIO`.
3. Un worker toma los pendientes, envía y guarda el CDR: código `0`/`4xxx` → `ACEPTADO` (las
   observaciones **no se reemiten**), `2xxx`/`3xxx` → `RECHAZADO` con el motivo.
4. Reintentos con backoff exponencial (máximo 3) y correlativo **no** se libera una vez persistido:
   el comprobante existe para el sistema aunque SUNAT no lo haya aceptado aún.
5. La comunicación con la OSE es el puerto `ISunatGateway`; su adaptador es lo primero que se
   implementará después de esta entrega.

## Consecuencias

**Positivas**

- Un fallo de red no pierde comprobantes ni duplica numeración.
- El estado del sistema es auditable: siempre se sabe si el XML se envió y qué respondió SUNAT.

**Negativas**

- Hace falta un worker y una cola persistente (SQLite basta en el despliegue local).
- La API debe exponer el estado `PENDIENTE_ENVIO` y no solo aceptado/rechazado.

## Verificación (cuando se implemente)

| Verificación | Criterio |
|---|---|
| No se reemite | un fallo de red deja el comprobante en `PENDIENTE_ENVIO` y no consume otro correlativo |
| CDR | código `0` y `4xxx` → `ACEPTADO`; `2xxx` → `RECHAZADO` |
| Persistencia | el XML validado está guardado antes de cualquier envío |
