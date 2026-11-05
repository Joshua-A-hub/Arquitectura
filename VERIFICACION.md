# Informe de verificación de la entrega

**Fecha:** 22 de octubre de 2026 · **Revisión:** 4 de noviembre de 2026 (correcciones según la rúbrica
del profesor)

**Método:** lectura del enunciado exigencia por exigencia → búsqueda de evidencia → ejecución de los
validadores → revisión cruzada contra la rúbrica de corrección → verificación con los **esquemas
oficiales de OASIS**.

---

## 1. Trazabilidad al enunciado

### 1.1 Los cuatro entregables

| # | Texto literal del examen | Evidencia | Estado |
|---|---|---|---|
| E1 | *"El Modelo de Dominio y Contratos (DTOs / Schemas)"* | 9 entidades + invariantes + diagrama de clases + 9 JSON Schemas | ✅ |
| E2 | *"Diagramas de Arquitectura MVC con visión a Hexagonal"* | 2 diagramas SVG+PNG, 11 ASR, 10 RNF, 3 ADR | ✅ |
| E3 | *"Especificación de Endpoints / Servicios (Contratos API)"* | OpenAPI 3.0.3: 12 rutas, 18 esquemas, JWT, catálogo de errores | ✅ |
| E4 | *"Matriz de Trazabilidad Normativa con cruces entre datos SUNAT y datos UBL"* | **63 cruces** + tabla de match de 47 campos | ✅ |

### 1.2 Las restricciones

| Restricción literal | Cómo se cumple | Estado |
|---|---|---|
| *"Legado y Migración de Datos … sin perder trazabilidad"* | mapeo campo a campo, estado OBSERVADA con motivo, idempotencia | ✅ |
| *"Normativa Tributaria Peruana … el catálogo 8"* | **catálogo 06** (identidad) y **catálogo 08** (sistema de ISC) modelados; 10 catálogos, 24 reglas | ✅ |
| *"monolítica limpia … MVC … Hexagonal o Clean"* | ASR verificables + diagramas + plan de migración | ✅ |
| *"Windows y Android … MSI … APK"* | decisión registrada, empaquetado con WiX (MSI real) | ✅ |
| *"detalle los casos posibles … Nubefact"* | 10 casos, 10 escenarios Gherkin, 17 inventariados, benchmark | ✅ |
| *"estudiando el archivo UBL-Invoice-2.1.xsd"* | **esquemas oficiales de OASIS en el repositorio** + XML validado contra ellos | ✅ |
| *"no es ponerte a codificar … antes de la primera línea"* | entrega = especificación; solo interfaces y validadores | ✅ |
| *"no quiere interfaz, solo specs"* | UI fuera de alcance en 4 documentos | ✅ |

---

## 2. Pruebas ejecutadas

| # | Prueba | Comando | Resultado |
|---|---|---|---|
| 1 | Contratos: 9 schemas, 3 ejemplos y OpenAPI | `validar_contratos.py` | **17/17**, 0 fallos |
| 2 | XML contra el esquema oficial + totales + RUC | `validar_xml_ubl.py` | **12/12**, 0 fallos |
| 3 | Verificación integral (enlaces, BOM, cifras, reglas, artefactos) | `verificar_entrega.py` | **8/8**, código 0 |
| 4 | Enlaces internos de 30 documentos | incluido en 3 | 0 roto |
| 5 | Esquemas oficiales de OASIS | `informe-xsd-oficial.md` | 16 archivos, compila, **XML válido** |
| 6 | Estructura del DOCX | reapertura con python-docx + zip | 94 párrafos, 10 tablas, íntegro |

### 2.1 Conformidad con UBL 2.1 (esquema oficial)

| Comprobación | Resultado |
|---|---|
| Archivos oficiales descargados | **16** (3 `maindoc` + 13 `common`), 2.82 MB, idénticos byte a byte |
| Compilación de `UBL-Invoice-2.1.xsd` | sin errores |
| Validación de `ejemplo-invoice.xml` | **válido, 0 errores** |
| Control negativo (elemento inventado, orden alterado, campo faltante, fecha mal formada) | los 4 rechazados |

### 2.2 Controles negativos de los validadores

| Experimento | Resultado |
|---|---|
| Quitar `serie_numero` del ejemplo | 16/17 · **código 1** · restaurar → 17/17 |
| Adulterar el IGV de cabecera del XML | la reconciliación lo detecta |
| Citar una regla inexistente | el verificador la marca |

---

## 3. Correcciones de la rúbrica (68 → objetivo 100)

La rúbrica del profesor descontó **32 puntos**. Cada descuento tiene ahora su corrección y su
evidencia:

| Descuento | Puntos | Corrección aplicada | Evidencia |
|---|:--:|---|---|
| No modela el ISC (catálogo 08) | −4 | `sistema_isc` (01/02/03), `monto_fijo_isc`, `precio_venta_publico`, **tres fórmulas** en RN-06, validación condicional, fila `TierRange` en la matriz | RN-06, DTO, matriz fila 38, catálogo 08 |
| XSD propio en vez del oficial | −4 | **16 esquemas oficiales** en `specs/contracts/ubl/oficial/`, decisión de generar clases con `xsdata`, validación antes de firmar | `informe-xsd-oficial.md`, ADR-0002 |
| Serie solo dígitos | −1 | `^[FB][A-Z0-9]{3}$` (F001, FC01, BA01) | RN-10, DTO, OpenAPI |
| Importes como `number` | −1 | importes como **string decimal** en DTOs, ejemplos y contrato | schemas + ejemplos |
| Valida después de firmar | −2 | orden: generar → **validar oficial** → firmar → verificar → enviar | RN-18, ADR-0002, secuencia |
| Códigos HTTP incompletos | −4 | 401/403 en todas las operaciones, **202 + ticket** en baja y migración, **422** para reglas, 400 en listados, `{id}` uniforme | `facturacion-api.yaml` |
| Sin libro 12.1 | −6 | `MovimientoAlmacen` con establecimiento, tabla 5, tabla 12, tabla 10, saldos, tabla 6 + DTO + endpoints | §2.8 del modelo, `09-libros-sunat.md` |
| Sin libro 14.1 | −6 | `RegistroVenta` + DTO + `GET /libros/14-1` | §2.9 del modelo, `09-libros-sunat.md` |
| Catálogo 8 mal usado y sin `TierRange` | −4 | renumerado 06 (identidad) / 08 (ISC) en todo el proyecto | catálogos, matriz, reglas, modelo |

**Total recuperable: 32 puntos.**

---

## 4. Límites conocidos (declarados)

| Tema | Situación |
|---|---|
| **Esquemas SUNAT** | se validó contra OASIS; los esquemas del SEE no se descargaron: la conformidad UBL está probada, la validación SUNAT real no |
| **Notas de crédito/débito** | se descargaron sus XSD oficiales, pero no se validó una instancia de ejemplo |
| **Firma criptográfica** | no se firma ni se verifica una firma real: es fase 2 |
| **DOCX** | no se inspeccionó visualmente (entorno sin renderizador); validado en estructura |
| **Código** | no hay lógica de negocio implementada: es una entrega de especificación |
| **Topología, numeración y outbox** | decisiones de diseño pendientes, documentadas en §4.1 de la revisión anterior |

---

## 5. Cómo reproducir

```bash
pip install -r requirements.txt
python validacion/verificar_entrega.py     # 8 comprobaciones, código 0
python validacion/validar_contratos.py     # 17 comprobaciones
python validacion/validar_xml_ubl.py       # 13 comprobaciones (incluye el esquema oficial)
```

---

## 6. Veredicto

La entrega **cubre los cuatro entregables y las restricciones del enunciado**, y su evidencia es
**ejecutable y falsificable**: 17 + 13 + 8 comprobaciones, con controles negativos, y el XML validado
contra los esquemas **oficiales** de OASIS.

Los 32 puntos que descontó la rúbrica tienen corrección y prueba. Lo que queda son límites de alcance
(fase 2 y validación SUNAT real), no contradicciones entre documentos.

---

## 7. Taller 2 (2.º parcial) — generación del XML desde el XSD

| Comprobación | Resultado |
|---|---|
| Clases generadas desde los XSD oficiales (xsdata) | 15 módulos, 3.1 MB, regenerables con scripts/generar_clases_ubl.ps1 |
| Pruebas unitarias de generación | **115** (cabecera, partes, líneas, tributos, totales, conformidad, regresión) |
| Pruebas unitarias de dominio | **44** (RUC, serie, IGV, ISC 01/02/03, ICBPER, letras, cuotas) |
| **Total de la suite** | **159 pruebas, 0 fallos** |
| Conformidad | los **8 escenarios** validan contra UBL-Invoice-2.1.xsd (NC/ND contra sus XSD) |
| Prueba de mutación | romper versión UBL, numeración de líneas o tasa de IGV hace fallar **21 pruebas** |
| CLI (segundo adaptador de entrada) | python -m src.cli generar-xml genera, valida y escribe el XML |

### Errores que encontraron las pruebas

| Error | Corrección |
|---|---|
| IGV desviado un céntimo (base redondeada antes de multiplicar) | se calcula sobre la base exacta y se redondea al final (RN-08) |
| Líneas exoneradas/inafectas declaraban el tributo `1000` | usan el tributo de su afectación (9997/9998/9995) |
| RN-02 rechazaba la exportación | la exportación admite al no domiciliado (catálogo 06 = 0) |
| Faltaban LineCountNumeric y AllowanceCharge que exige la matriz | se añadieron al generador y sus pruebas |
| PriceAmount con 2 decimales no cuadraba con la cantidad | valor unitario con 6 decimales |
| Las cuotas no se validaban contra el total | Comprobante exige que sumen el importe total (RN-16) |

Detalle: [docs/taller-2-generacion-xml.md](docs/taller-2-generacion-xml.md).
