# Casos de uso — Sistema de Facturación Electrónica

Derivados del caso (sección 3: *"la gerencia desea que detalle los casos posibles"*). Los actores y
flujos se contrastaron con la operación típica de una facturadora electrónica (patrón Nubefact:
emisión → envío → CDR → notas → reportes).

---

## 1. Actores

| Actor | Descripción | Interés |
|---|---|---|
| **Operador de almacén** | Registra ventas y emite comprobantes | rapidez, no equivocarse |
| **Cajero / vendedor** | Emite boletas y facturas en mostrador | fluidez, impresión |
| **Administrador / contador** | Consulta, anula, reporta | cumplimiento tributario |
| **Sistema SUNAT / OSE** | Recibe el XML y devuelve CDR | validez formal |
| **Proceso de migración** | Carga históricos del legado | no perder información |

## 2. Mapa de casos de uso

```text
                    ┌────────────────────────────┐
                    │  Sistema de Facturación     │
   Operador ───────▶│ CU-01 Emitir factura        │
   Cajero   ───────▶│ CU-02 Emitir boleta         │
   Contador ───────▶│ CU-03 Emitir nota de crédito│
                    │ CU-04 Emitir nota de débito │
                    │ CU-05 Consultar comprobante │
                    │ CU-06 Dar de baja           │
                    │ CU-07 Descargar XML/PDF     │
                    │ CU-08 Migrar fichas legadas │
                    │ CU-09 Mantener clientes     │
                    │ CU-10 Mantener productos    │
                    └──────────┬─────────────────┘
                               │
                    ┌──────────▼─────────────────┐
                    │  SUNAT / OSE (externo)      │
                    └────────────────────────────┘
```

| ID | Caso de uso | Actor | Precondición | Salida |
|---|---|---|---|---|
| CU-01 | Emitir factura | Operador | cliente con RUC válido | comprobante ACEPTADO + XML |
| CU-02 | Emitir boleta | Cajero | — (admite consumidor final) | comprobante ACEPTADO |
| CU-03 | Emitir nota de crédito | Contador | comprobante ACEPTADO | nota + saldo actualizado |
| CU-04 | Emitir nota de débito | Contador | comprobante ACEPTADO | nota + saldo actualizado |
| CU-05 | Consultar comprobante | Todos | — | estado y detalle |
| CU-06 | Dar de baja | Contador | comprobante ACEPTADO | estado BAJA |
| CU-07 | Descargar XML/PDF | Todos | comprobante emitido | archivo |
| CU-08 | Migrar fichas | Administrador | archivo del legado | reporte migradas/observadas |
| CU-09 | Mantener clientes | Administrador | — | cliente creado/actualizado |
| CU-10 | Mantener productos | Administrador | — | producto con afectación |

## 3. Escenarios (Gherkin)

### CU-01 — Emitir factura

```gherkin
Escenario: Emisión exitosa de una factura
  Dado un cliente con RUC "20512345671" y razón social "DISTRIBUIDORA SELVA SAC"
  Y un detalle de 3 líneas con afectación al IGV "10", "20" y "10"
  Cuando el operador solicita emitir una factura con serie "F001"
  Entonces el sistema asigna el número "F001-00000001"
  Y calcula el IGV de las líneas gravadas al 18%
  Y el importe total es la suma de operaciones más tributos
  Y el comprobante queda en estado "ACEPTADO"
  Y el XML generado valida contra el XSD de UBL 2.1
```

```gherkin
Escenario: Rechazo por RUC inválido
  Dado un cliente con tipo de documento "6" y número "20512345670"
  Y ese número no supera la validación del dígito verificador
  Cuando el operador intenta emitir la factura
  Entonces el sistema responde error de negocio en el campo "cliente.numero_documento"
  Y no se genera ningún comprobante
  Y el correlativo no se consume
```

### CU-02 — Emitir boleta a consumidor final

```gherkin
Escenario: Boleta sin documento de identidad
  Dado un cliente con tipo de documento "0" y número "0"
  Cuando el cajero emite una boleta con serie "B001"
  Entonces el comprobante se emite con número "B001-00000001"
  Y el XML se genera sin datos de domicilio del receptor
```

### CU-03 — Nota de crédito total

```gherkin
Escenario: Anulación de una factura aceptada
  Dado una factura "F001-00000001" en estado "ACEPTADO" por S/ 1,180.00
  Cuando el contador emite una nota de crédito con motivo "01" (anulación)
  Entonces la nota referencia a la factura original
  Y su importe no supera el saldo de la factura
  Y el comprobante original no cambia de estado
```

### CU-06 — Baja

```gherkin
Escenario: Dar de baja un comprobante aceptado
  Dado un comprobante en estado "ACEPTADO"
  Cuando el contador registra la baja con un motivo
  Entonces el estado cambia a "BAJA"
  Y el comprobante no puede volver a "ACEPTADO"
```

```gherkin
Escenario: No se puede dar de baja un borrador
  Dado un comprobante en estado "BORRADOR"
  Cuando se intenta dar de baja
  Entonces el sistema responde error de negocio
```

### CU-08 — Migración

```gherkin
Escenario: Migración de fichas del legado
  Dado un lote de 100 fichas con fecha, producto y nro_documento
  Cuando el administrador ejecuta la migración
  Entonces cada ficha aparece en el resultado como "MIGRADA" u "OBSERVADA"
  Y la suma de migradas y observadas es 100
  Y las fichas con producto no identificado quedan "OBSERVADA" con su motivo
  Y ninguna ficha se pierde
```

```gherkin
Escenario: Reproceso idempotente
  Dado un lote que ya fue migrado
  Cuando se vuelve a ejecutar la migración
  Entonces no se crean movimientos duplicados
  Y todas las fichas siguen reportándose como "MIGRADA"
```

### Validación tributaria transversal

```gherkin
Escenario: Cálculo del ICBPER
  Dado una línea de 20 bolsas plásticas
  Cuando se calcula el comprobante
  Entonces el ICBPER de la línea es S/ 10.00 (0.50 por bolsa)
  Y ese monto se suma al importe total sin afectar la base del IGV
```

```gherkin
Escenario: Comprobante exonerado no genera IGV
  Dado una línea con afectación "20" (exonerado)
  Cuando se calcula el comprobante
  Entonces el IGV de la línea es 0.00
  Y el importe se acumula en operaciones exoneradas
```

## 4. Trazabilidad casos de uso → requisitos

| Caso | Requisitos | Entregable |
|---|---|---|
| CU-01, CU-02 | REQ-03, REQ-04, REQ-05 | E1, E3, E4 |
| CU-03, CU-04 | REQ-05, REQ-06 | E1, E4 |
| CU-05, CU-07 | REQ-05 | E3 |
| CU-06 | REQ-02 | E1 |
| CU-08 | REQ-01 | E1 · `docs/arquitectura/05-migracion-legado.md` |
| CU-09, CU-10 | REQ-03, REQ-04 | E1 |
| Transversal | REQ-07, REQ-08, REQ-09, REQ-10 | E2, `specs/architecture/mvc-hexagonal.md` |

---

## 5. Inventario de casos posibles y su alcance

El enunciado pide *"detallar los casos posibles"*. Este es el inventario completo, incluidos los que
**no** se implementan y por qué: declarar el alcance también es parte de especificar.

| Caso identificado | Alcance | Motivo / nota |
|---|---|---|
| Emitir factura | **Incluido** | CU-01 |
| Emitir boleta (con y sin documento) | **Incluido** | CU-02 |
| Emitir nota de crédito / débito | **Incluido** | CU-03, CU-04 |
| Consultar comprobante y estado del CDR | **Incluido** | CU-05 |
| Dar de baja un comprobante | **Incluido** (unitaria) | CU-06 |
| Descargar XML / constancia | **Incluido** | CU-07 |
| Migrar fichas del legado | **Incluido** | CU-08 |
| Mantener clientes y productos | **Incluido** | CU-09, CU-10 |
| Resumen diario de boletas | **Fase 2** | requiere proceso programado ante SUNAT |
| Comunicación masiva de bajas | **Fase 2** | proceso por lote |
| Reportes y exportación contable | **Fase 2** | no es emisión |
| Comprobantes de retención y percepción | **Fuera** | régimen distinto, no lo pide el caso |
| Guías de remisión | **Fuera** | otro tipo de documento (DispatchAdvice) |
| Facturación con detracción | **Fuera** | exige depósito en cuenta del Banco de la Nación |
| Multiempresa / multi-RUC | **Fuera** | un emisor por despliegue en esta fase |
| Portal del cliente final | **Fuera** | la entrega es operativa (almacén/administración) |
| Contingencia por caída de SUNAT | **Fuera** | protocolo administrativo, no del sistema |

**Resumen:** 10 casos incluidos · 3 diferidos a fase 2 · 6 declarados fuera de alcance.

> Criterio aplicado: incluir un caso cuesta diseño, pruebas y soporte; dejarlo fuera sin decirlo cuesta
> credibilidad. Por eso los descartados están escritos con su motivo.
