# Tests

En Spec-Driven Development los tests se organizan por **qué validan**, no por carpeta del código.

```text
tests/
├── acceptance/   valida los escenarios Gherkin de specs/features/
├── integration/  valida la interacción entre adaptadores (repositorio, XML, OSE)
├── unit/         valida reglas y cálculos aislados (sin HTTP, sin base de datos)
├── mocks/        datos estáticos que simulan la persistencia
└── README.md     esta guía
```

## Estado en esta fase

El examen pide **especificaciones**, no implementación, así que los tests están **especificados**
(escenarios Gherkin + IDs QA-01..QA-24) pero todavía no codificados: no existe lógica de negocio que
probar. El mock ya está listo (`tests/mocks/mock_db.py`).

Lo que **sí** es ejecutable hoy es la validación de los contratos, que no depende de la lógica:

```bash
python validacion/validar_contratos.py
```

## Mapa de pruebas comprometidas (fase 2)

| Nivel | Archivo previsto | Qué valida | Origen |
|---|---|---|---|
| Unitario | `unit/test_calculadora_tributos.py` | IGV 18%, exonerado, ISC, ICBPER, redondeo | RN-04..RN-09, QA-17..QA-19 |
| Unitario | `unit/test_reglas.py` | RUC (módulo 11), catálogo 8, series, fechas | RN-01..RN-13, QA-08..QA-10 |
| Unitario | `unit/test_numeracion.py` | correlativo por serie, sin huecos | RN-10..RN-12, QA-02 |
| Unitario | `unit/test_ubl_builder.py` | namespaces, orden de elementos, rutas | perfil UBL, QA-21 |
| Aceptación | `acceptance/test_emision_factura.py` | CU-01 completo contra la API | Gherkin CU-01 |
| Aceptación | `acceptance/test_emision_boleta.py` | CU-02 consumidor final | Gherkin CU-02 |
| Aceptación | `acceptance/test_notas.py` | CU-03/CU-04, referencia y saldo | Gherkin CU-03 |
| Aceptación | `acceptance/test_baja.py` | CU-06 y transición de estados | Gherkin CU-06 |
| Aceptación | `acceptance/test_migracion.py` | lote, observadas, idempotencia | RN-22, QA-23/24 |
| Integración | `integration/test_repositorio_sqlite.py` | persistencia real y transacción de correlativo | RN-11, RN-12 |
| Integración | `integration/test_ose_gateway.py` | envío simulado y lectura de CDR | RN-19, QA-22 |

## Reglas de los tests en este proyecto

1. Un test por escenario Gherkin; el nombre del test cita el ID (ej. `test_cu01_emision_factura`).
2. Prohibido tocar un test para que pase: si falla, se corrige el código o el contrato (en ese orden
   inverso si el contrato estaba mal).
3. Los tests usan `mock_db.reiniciar()` en un fixture para ser independientes entre sí.
4. El caso negativo siempre existe: un escenario que debe **fallar** (RUC inválido, XML inválido).
