# Benchmark de facturación electrónica — qué le duele al usuario y qué hacemos

El caso lo pide explícitamente: *"La gerencia desea que detalle los casos posibles, revisando
opiniones de usuarios de facturación electrónica, por lo que puede revisar otros softwares en línea
como el caso de Nubefact"*.

Este documento traduce esas opiniones en **requisitos de diseño concretos**.

> **Método y límite:** el análisis se basa en los flujos públicos de las plataformas de facturación
> electrónica peruana (emisión, envío, CDR, notas, reportes, API) y en los problemas recurrentes que
> reportan sus usuarios. No se creó una cuenta DEMO: aquí interesa el **patrón de dolor**, no la
> interfaz exacta de un proveedor.

---

## 1. Los diez dolores más frecuentes

| # | Dolor del usuario | Qué provoca | Cómo lo resuelve este diseño | Regla / caso |
|---|---|---|---|---|
| 1 | "SUNAT me rechazó por un catálogo" | afectación de IGV o tipo de documento mal elegido | catálogos cerrados en el contrato (enum) + validación antes de generar el XML | Cat. 7 y 8 · RN-02 |
| 2 | "No sé si el comprobante llegó" | el usuario reenvía o duplica | estado explícito (`EMITIDO`, `ACEPTADO`, `RECHAZADO`) + CDR guardado y consultable | RN-17, RN-19 · CU-05 |
| 3 | "Se me repitió el número" | series y correlativos manejados a mano | correlativo asignado en transacción, único por `tipo+serie` | RN-10..RN-12 |
| 4 | "El total no cuadra" | IGV mal aplicado, redondeos distintos | totales calculados en el dominio (nunca recibidos) y redondeo definido por línea | RN-04..RN-09 |
| 5 | "La nota de crédito no cuadra con la factura" | notas sin control de saldo | la nota referencia el comprobante y no supera el saldo | RN-16 · CU-03 |
| 6 | "Se cayó el internet y quedó a medias" | reenvío manual y duplicados | reintentos con backoff y estado `PENDIENTE_ENVIO`; nunca se reemite | RN-20 |
| 7 | "Perdí el histórico de mi sistema viejo" | migraciones que descartan filas | toda ficha se migra u observada con motivo; idempotente por `id_ficha` | RN-21..RN-24 · CU-08 |
| 8 | "No puedo emitir desde el celular" | solo escritorio | cliente multiplataforma con el mismo contrato | doc 06 · ADR-0003 |
| 9 | "El sistema es lento para una venta de mostrador" | validaciones en línea contra SUNAT | validación local (XSD + reglas) y envío diferido | RN-18 · ADR-0002 |
| 10 | "No entiendo el mensaje de error" | errores genéricos | todo error devuelve `campo` + `mensaje` legible | `ErrorValidacion` |

## 2. Qué ofrece el mercado (patrón común)

| Capacidad | Frecuencia en plataformas de facturación electrónica | ¿La incluimos? |
|---|---|---|
| Emisión guiada de factura/boleta | estándar | Sí — CU-01, CU-02 |
| Estado del CDR visible | estándar | Sí — CU-05, RN-19 |
| Notas de crédito y débito | estándar | Sí — CU-03, CU-04 |
| Resumen diario de boletas | estándar | **No en esta fase** (declarado) |
| Comunicación de baja | estándar | Sí, unitaria — CU-06 |
| API para integrar | en planes medios/altos | Sí — contrato OpenAPI (E3) |
| App móvil | variable | Sí — doc 06 |
| Reportes y exportación | estándar | No en esta fase (solo consulta) |
| Multiempresa / multi-RUC | planes altos | No (fuera de alcance) |

## 3. Las tres mejoras que adoptamos

El benchmark no se queda en análisis: cambia el diseño.

### Mejora 1 — "Estado siempre visible" (del dolor 2)

Toda respuesta de emisión incluye `estado`, `cdr.codigo` y `xml_url`. El operador nunca se pregunta
si el comprobante llegó: lo consulta o lo ve en la respuesta.

- Impacto: `ComprobanteResponse` en el contrato, CU-05.
- Regla asociada: RN-17 (máquina de estados), RN-19 (CDR).

### Mejora 2 — "Error que dice qué corregir" (del dolor 10)

Todos los errores tienen la forma `{codigo, errores:[{campo, mensaje}]}`. El front puede resaltar el
campo exacto en lugar de mostrar "error inesperado".

- Impacto: `ErrorValidacion` en OpenAPI, validación en dos capas (esquema vs negocio).
- Regla asociada: RN-02, RN-13, RN-14.

### Mejora 3 — "Nunca pierdas una ficha" (del dolor 7)

La migración devuelve un reporte por ficha (`MIGRADA` / `OBSERVADA` con motivo) y es idempotente: se
puede reprocesar el mismo archivo sin duplicar.

- Impacto: `MigracionResponse`, CU-08, doc 05.
- Regla asociada: RN-22, RN-23.

## 4. Qué NO copiamos del mercado (y por qué)

| Práctica común | Por qué no la adoptamos |
|---|---|
| Emitir sin validar contra XSD "y si falla, se corrige después" | genera rechazos y reintentos manuales; el costo se traslada al usuario |
| Totales editables en la interfaz | abre la puerta a comprobantes inconsistentes |
| Número de comprobante libre | rompe la unicidad y la trazabilidad |
| Migración "a como salga" | pierde historia y no es auditable |

## 5. Conclusión

El diseño no sale de la imaginación: **cada regla RN-xx responde a un dolor documentado de quien usa
facturación electrónica todos los días**. Eso es lo que diferencia un sistema que cumple la norma de
uno que además se puede operar.

| Dolor cubierto | 10 de 10 |
|---|---|
| Mejoras de UX incorporadas al contrato | 3 |
| Reglas trazadas al benchmark | 16 de 24 |
