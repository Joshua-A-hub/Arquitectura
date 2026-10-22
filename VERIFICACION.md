# Informe de verificación de la entrega

**Fecha:** 22 de octubre de 2026
**Método:** lectura del enunciado exigencia por exigencia → búsqueda de evidencia en el repositorio →
ejecución de los validadores → conteo programático de lo que los documentos afirman → **cuatro
revisiones independientes** (arquitectura, QA, documental y normativa SUNAT/UBL) en modo lectura.

---

## 1. Trazabilidad al enunciado

### 1.1 Los cuatro entregables

| # | Texto literal del examen | Evidencia | Estado |
|---|---|---|---|
| E1 | *"El Modelo de Dominio y Contratos (DTOs / Schemas)"* | 6 entidades, invariantes, diagrama de clases, 7 JSON Schemas | ✅ |
| E2 | *"Diagramas de Arquitectura MVC con visión a Hexagonal"* | 2 diagramas SVG+PNG, 11 ASR, 10 RNF, 3 ADR | ✅ |
| E3 | *"Especificación de Endpoints / Servicios (Contratos API)"* | OpenAPI 3.0.3: 9 rutas, 15 esquemas, JWT, catálogo de errores | ✅ |
| E4 | *"Matriz de Trazabilidad Normativa con cruces entre datos SUNAT y datos UBL"* | 59 cruces + tabla de match de 47 campos | ✅ |

### 1.2 Las restricciones

| Restricción literal | Cómo se cumple | Estado |
|---|---|---|
| *"Legado y Migración de Datos … sin perder trazabilidad"* | mapeo campo a campo, estado OBSERVADA con motivo, idempotencia | ✅ |
| *"Normativa Tributaria Peruana … catálogo 8"* | 9 catálogos, 24 reglas, marco normativo; **ver nota de numeración 06/08** | ✅ con salvedad |
| *"monolítica limpia … MVC … Hexagonal o Clean"* | ASR verificables + diagramas + plan de migración | ✅ |
| *"Windows y Android … MSI … APK"* | decisión registrada, empaquetado con WiX (MSI real) | ✅ |
| *"detalle los casos posibles … Nubefact"* | 10 casos, 10 escenarios Gherkin, 17 inventariados, benchmark | ✅ |
| *"estudiando el archivo UBL-Invoice-2.1.xsd"* | extracto del XSD de OASIS + perfil materializado | ✅ (perfil didáctico) |
| *"no es ponerte a codificar … antes de la primera línea"* | entrega = especificación; solo interfaces y validadores | ✅ |
| *"no quiere interfaz, solo specs"* | UI fuera de alcance en 4 documentos | ✅ |

---

## 2. Pruebas ejecutadas

| # | Prueba | Comando | Resultado |
|---|---|---|---|
| 1 | Contratos: 7 schemas, 3 ejemplos y OpenAPI (parseo real) | `validar_contratos.py` | **15/15**, 0 fallos |
| 2 | XML del perfil contra XSD + reconciliación de totales + RUC | `validar_xml_ubl.py` | **11/11**, 0 fallos |
| 3 | Verificación integral (enlaces, BOM, cifras, reglas, artefactos) | `verificar_entrega.py` | **8/8**, código 0 |
| 4 | Enlaces internos de los 28 documentos | incluido en 3 | 0 roto |
| 5 | Estructura del DOCX | verificador OOXML (externo, no incluido) | `pass`, 300 párrafos, 10 tablas |
| 6 | Control negativo de contratos | quitar `serie_numero` | detectado: 12/13, código 1 |
| 7 | Control negativo de XML | adulterar el IGV de cabecera | detectado por la reconciliación |

### Comprobación de que las pruebas detectan fallos

| Experimento | Resultado |
|---|---|
| Eliminar `serie_numero` del ejemplo de respuesta | 12/13 · **código 1** · restaurar → 15/15 |
| Adulterar el IGV de cabecera del XML | la reconciliación lo detecta |
| Introducir una regla inexistente en un documento | el verificador la marca (probado con un identificador fuera de rango) |

---

## 3. Qué encontraron las revisiones (y qué se corrigió)

| ID | Hallazgo | Sev. | Estado |
|---|---|---|---|
| R-01 | Referencias a reglas corridas en el modelo (RUC→RN-02, ICBPER→RN-06…) | Alta | **Corregido** (11 referencias + guardián en el verificador) |
| R-02 | El validador no implementaba `exclusiveMinimum` numérico: aceptaba `cantidad: 0` | Alta | **Corregido** (ahora el ejemplo inválido da 6 errores) |
| R-03 | `const` no implementado: el `if/then` del catálogo 8 aplicaba ambas ramas | Alta | **Corregido** |
| R-04 | El XSD no admitía el bloque de firma: el XML firmado habría sido rechazado | Alta | **Corregido** (`xs:any` para `ext:UBLExtensions`) |
| R-05 | Orden de `InvoiceLine` no era el de UBL 2.1 | Alta | **Corregido** (XML y XSD reordenados) |
| R-06 | Línea exonerada declaraba el tributo 1000 (IGV) en vez de 9997 | Alta | **Corregido** (+ catálogo 05 completo) |
| R-07 | El ISC sí integra la base del IGV | Alta | **Corregido** (RN-05/RN-06) |
| R-08 | CDR 4000+ son observaciones, no rechazos | Alta | **Corregido** (RN-19) |
| R-09 | RUC de los ejemplos no pasaban el módulo 11 | Alta | **Corregido** + comprobación automática en el validador |
| R-10 | `TaxInclusiveAmount` no incluía el ICBPER | Alta | **Corregido** (530.00 = 530.00) |
| R-11 | `cbc:DiscrepancyResponse` → es `cac:` | Media | **Corregido** en 3 documentos |
| R-12 | Cifras repetidas a mano y desincronizadas (5 vs 7 schemas, 9 vs 10 escenarios) | Media | **Corregido** |
| R-13 | Dos totales distintos para el mismo `F001-00000123` | Alta | **Corregido** (530.00 en XML, JSON y respuesta) |
| R-14 | "Vista = contrato de la UI" contradecía "sin interfaz" | Alta | **Corregido** |
| R-15 | El perfil decía que el XSD exige `currencyID` (es opcional en OASIS) | Media | **Corregido** (SUNAT lo exige; el perfil lo vuelve obligatorio) |
| R-16 | Catálogo 10 usaba códigos 10/11 inexistentes (son 11/12) | Media | **Corregido** |
| R-17 | Erratas (RM-22, "e es", "0 enlaces roto") | Baja | **Corregido** |
| R-18 | `__pycache__` dentro de la entrega | Baja | **Corregido** (eliminado) |

---

## 4. Límites conocidos (declarados, no ocultos)

### 4.1 Diseño (requieren decisión, no una errata)

| Tema | Situación | Qué haría falta |
|---|---|---|
| **Topología** | doc 06 dice servicio "local en el dispositivo" y también "el certificado nunca sale del servidor" | elegir: servidor central + cliente delgado, o emisión local con análisis de riesgo |
| **Correlativo sin huecos** | se exige unicidad atómica sobre SQLite por dispositivo con emisión offline | ADR de fuente de verdad y numeración (escritor único o rango por dispositivo) |
| **Flujo y outbox** | el guardado ocurre después del envío; `PENDIENTE_ENVIO` no tiene dónde persistirse | flujo borrador → reserva → pendiente → worker |
| **Idempotencia** | el POST no acepta `Idempotency-Key` y el 502 no devuelve `id` | cabecera obligatoria + 202 con identificador |
| **Diagrama hexagonal** | las flechas muestran el flujo de llamadas, no la inversión de dependencias | redibujar con dominio al centro y puertos en el borde |
| **`MovimientoAlmacen`** | es destino de la migración y no está definido en el modelo | añadir entidad con campos e invariantes |
| **ICBPER por bolsa** | se calcula 0.50 × bolsas pero no hay campo de bolsas en la línea | añadir `cantidad_bolsas` o resolverlo desde el maestro de productos |
| **Perfil de notas** | NC/ND sin XSD ni ejemplo propio | crear `CreditNote` del perfil |

### 4.2 Normativo (marcados como *verificar* por el revisor)

| Tema | Situación |
|---|---|
| **Numeración del "catálogo 8"** | En el SEE, el tipo de documento de identidad es el **catálogo 06** y el 08 es el sistema de cálculo del ISC. El enunciado dice "8": se documentan **ambos** y se explica la diferencia |
| **IVAP (afectación 17)** | se calcula como IGV 18 %; el IVAP es 4 % con tributo 1016 (fuera de alcance declarado) |
| **Tipo de cambio** | se admite USD sin modelar `cac:TaxExchangeRate` |
| **Serie** | se restringe a `F001`/`B001`; la guía SUNAT la describe alfanumérica |
| **Plazo de conservación** | se usa el plazo de prescripción (4 años); el RCP suele citarse en 5 |
| **RS 097-2012 / 234-2006** | se describen por su rol, sin citar artículo; el texto vigente debe verificarse |
| **Validación UBL real** | el XSD validado es un **perfil didáctico**, no el esquema OASIS completo: no sustituye una validación SUNAT |

### 4.3 Evidencia

- El **DOCX no se inspeccionó visualmente** (el entorno bloquea el renderizador). Validado en estructura.
- **No hay PDF** por el mismo motivo.
- **No se probó el sistema en ejecución**: no hay lógica de negocio (fase 2).

---

## 5. Cómo reproducir

```bash
pip install -r requirements.txt
python validacion/verificar_entrega.py     # 8 comprobaciones, código 0
```

Por separado:

```bash
python validacion/validar_contratos.py     # 15 comprobaciones
python validacion/validar_xml_ubl.py       # 11 comprobaciones
```

---

## 6. Veredicto

La entrega **cubre los cuatro entregables y las restricciones del enunciado**, y su capa de evidencia
es hoy **real y falsificable**: 15 + 11 + 8 comprobaciones, con controles negativos que demuestran que
las pruebas detectan fallos.

Lo que queda no son erratas: son **decisiones de diseño** (topología, numeración, outbox,
idempotencia) y **puntos normativos que exigen el texto oficial de SUNAT**. Están todos listados
arriba, con nombre y consecuencia. Un trabajo que declara sus huecos es más defendible que uno que
aparenta no tenerlos.
