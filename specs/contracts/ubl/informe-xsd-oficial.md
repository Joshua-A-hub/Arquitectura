# Informe de validación con esquemas oficiales OASIS UBL 2.1

**Proyecto:** facturación electrónica SUNAT / UBL 2.1
**Fecha de ejecución:** 2026-11-04 (America/Lima)
**Alcance:** descargar los esquemas oficiales de OASIS, compilarlos con lxml y validar
`specs/contracts/ubl/ejemplo-invoice.xml` contra ellos, sin modificar el XML ni el perfil propio.

| Dato | Valor |
|---|---|
| Origen de los esquemas | `https://docs.oasis-open.org/ubl/os-UBL-2.1/xsd/` |
| Release declarado en los XSD | UBL 2.1 OS — *Release Date: 04 November 2013*, generado `2013-10-31 17:17z` |
| Esquema raíz compilado | `maindoc/UBL-Invoice-2.1.xsd` |
| Namespace destino | `urn:oasis:names:specification:ubl:schema:xsd:Invoice-2` |
| Intérprete | Python 3.13 (`C:\Users\benny\AppData\Local\Programs\Python\Python313\python.exe`) |
| `PYTHONPATH` | `C:\Users\benny\Desktop\Arquitectura\_tools` |
| lxml | 6.1.3 |
| Destino local | `specs/contracts/ubl/oficial/maindoc/` y `specs/contracts/ubl/oficial/common/` |

---

## 1. Resumen ejecutivo

1. Se descargaron **16 archivos** (3 `maindoc` + 13 `common`), **2 954 880 bytes (2.82 MB)** en total,
   con **0 fallos**. Todos respondieron **HTTP 200**, todos son XSD parseables (ninguno es una página
   HTML de error) y los 16 resultaron **idénticos byte a byte** al volver a descargarlos.
2. El esquema oficial **compila sin errores** (`etree.XMLSchema` → 0 entradas en el `error_log`).
3. El ejemplo `ejemplo-invoice.xml` **VALIDA contra el esquema oficial** (0 errores).
4. **No hay diferencias de conformidad**: el ejemplo es estructuralmente conforme a UBL 2.1.
   La lista de diferencias del apartado 6 está, por tanto, vacía; en su lugar se documenta
   (medido, no supuesto) **qué es lo que el XSD oficial no restringe**.
5. El perfil propio `xsd/Invoice-2-profile.xsd` queda como **restricción adicional** (subconjunto),
   **no como sustituto** del esquema oficial. Evidencia en el apartado 7.

---

## 2. Inventario de archivos descargados

Prefijo de origen común: `https://docs.oasis-open.org/ubl/os-UBL-2.1/xsd/` + ruta relativa indicada.
Cada archivo se verificó por tamaño, por contenido (parsea como XSD) y contra el servidor (ver 2.1).

| # | Archivo (ruta relativa) | Bytes | SHA-256 (16 primeros) | Rol | Origen |
|---:|---|---:|---|---|---|
| 1 | `maindoc/UBL-Invoice-2.1.xsd` | 60 178 | `40fae8cb436f3a95` | Esquema raíz — Factura | `…/xsd/maindoc/UBL-Invoice-2.1.xsd` |
| 2 | `maindoc/UBL-CreditNote-2.1.xsd` | 57 697 | `a54651b1225052f8` | Esquema raíz — Nota de crédito | `…/xsd/maindoc/UBL-CreditNote-2.1.xsd` |
| 3 | `maindoc/UBL-DebitNote-2.1.xsd` | 55 434 | `295d142102a2a0cd` | Esquema raíz — Nota de débito | `…/xsd/maindoc/UBL-DebitNote-2.1.xsd` |
| 4 | `common/UBL-CommonAggregateComponents-2.1.xsd` | 2 420 444 | `939172ad8dd057cd` | Componentes agregados (cac) | `…/xsd/common/UBL-CommonAggregateComponents-2.1.xsd` |
| 5 | `common/UBL-CommonBasicComponents-2.1.xsd` | 219 895 | `bd4ad043ee1d9da1` | Componentes básicos (cbc) | `…/xsd/common/UBL-CommonBasicComponents-2.1.xsd` |
| 6 | `common/UBL-CommonExtensionComponents-2.1.xsd` | 9 491 | `ad7a4e490978adfb` | Bloque `ext:UBLExtensions` | `…/xsd/common/UBL-CommonExtensionComponents-2.1.xsd` |
| 7 | `common/UBL-ExtensionContentDataType-2.1.xsd` | 4 314 | `fcee77a11870208e` | Tipo del contenido de extensión | `…/xsd/common/UBL-ExtensionContentDataType-2.1.xsd` |
| 8 | `common/UBL-CommonSignatureComponents-2.1.xsd` | 5 548 | `3db472305f029bba` | Contenedor de firma | `…/xsd/common/UBL-CommonSignatureComponents-2.1.xsd` |
| 9 | `common/UBL-SignatureAggregateComponents-2.1.xsd` | 7 784 | `17bb6b62d709b4fd` | Agregados de firma | `…/xsd/common/UBL-SignatureAggregateComponents-2.1.xsd` |
| 10 | `common/UBL-SignatureBasicComponents-2.1.xsd` | 4 207 | `cef924d7ba3d1d8a` | Básicos de firma | `…/xsd/common/UBL-SignatureBasicComponents-2.1.xsd` |
| 11 | `common/UBL-xmldsig-core-schema-2.1.xsd` | 10 750 | `101909c9f06456d6` | XMLDSig (`ds:`) | `…/xsd/common/UBL-xmldsig-core-schema-2.1.xsd` |
| 12 | `common/UBL-XAdESv132-2.1.xsd` | 21 664 | `a4f726bcf8cc3f7d` | XAdES v1.3.2 | `…/xsd/common/UBL-XAdESv132-2.1.xsd` |
| 13 | `common/UBL-XAdESv141-2.1.xsd` | 1 316 | `1fa4625e9cefcb7a` | XAdES v1.4.1 | `…/xsd/common/UBL-XAdESv141-2.1.xsd` |
| 14 | `common/UBL-UnqualifiedDataTypes-2.1.xsd` | 27 300 | `09052d406b4293e2` | Tipos sin cualificar | `…/xsd/common/UBL-UnqualifiedDataTypes-2.1.xsd` |
| 15 | `common/UBL-QualifiedDataTypes-2.1.xsd` | 3 590 | `7dcb156e610239c9` | Tipos cualificados | `…/xsd/common/UBL-QualifiedDataTypes-2.1.xsd` |
| 16 | `common/CCTS_CCT_SchemaModule-2.1.xsd` | 45 268 | `dd546e4809df86b6` | Módulo CCTS de UN/CEFACT | `…/xsd/common/CCTS_CCT_SchemaModule-2.1.xsd` |
| | **Total (16 archivos)** | **2 954 880** | | | |

### 2.1 Verificación de las descargas

No se dio por buena ninguna descarga sin comprobarla:

- **Estado HTTP:** 200 en los 16 archivos (0 errores, 0 reintentos necesarios).
- **Tamaño:** contrastado con el servidor mediante una segunda descarga completa:
  16/16 con el mismo número de bytes. `UBL-CommonAggregateComponents-2.1.xsd` llegó con
  **2 420 444 bytes (2.31 MiB)**, coherente con el valor esperado (~2.4 MB); ningún archivo
  quedó en el rango de "pocos KB" ni con pinta de HTML.
- **Contenido:** los 16 parsean como XML con raíz `xs:schema`, sin `<!doctype html>` ni `<html>`.
  Nº de declaraciones `xsd:element`: `CommonAggregateComponents` = 2 804, `CommonBasicComponents` = 873,
  `Invoice` = 55.
- **Integridad byte a byte:** los 16 archivos locales son idénticos (`==` sobre bytes) a una
  segunda descarga independiente; además, el **MD5 local coincide con el `ETag` del servidor**
  en los 16 casos (p. ej. `UBL-CommonAggregateComponents-2.1.xsd` → `1b5be93364f2b7508d106cfa8bc704c1`).
  Es decir: los XSD guardados **no se han editado ni reformateado**; son los originales de OASIS.
- **Dependencias:** el cierre se calculó de forma recursiva leyendo los `xsd:import`/`xsd:include`
  realmente presentes en cada archivo (no una lista prefijada). No quedó ningún `schemaLocation`
  sin resolver ni import sin `schemaLocation`.

### 2.2 Por qué son 13 `common` y no 11

La cadena de dependencias real arrastra los esquemas de firma, que no son opcionales para el
compilador aunque el ejemplo no firme:

```
maindoc/UBL-Invoice-2.1.xsd
    → ../common/UBL-CommonAggregateComponents-2.1.xsd
    → ../common/UBL-CommonBasicComponents-2.1.xsd
    → ../common/UBL-CommonExtensionComponents-2.1.xsd
          → UBL-ExtensionContentDataType-2.1.xsd
                → UBL-CommonSignatureComponents-2.1.xsd
                      → UBL-SignatureAggregateComponents-2.1.xsd
                            → UBL-SignatureBasicComponents-2.1.xsd
                            → UBL-xmldsig-core-schema-2.1.xsd   (http://www.w3.org/2000/09/xmldsig#)
                            → UBL-XAdESv132-2.1.xsd             (http://uri.etsi.org/01903/v1.3.2#)
                            → UBL-XAdESv141-2.1.xsd             (http://uri.etsi.org/01903/v1.4.1#)
                                  → UBL-XAdESv132-2.1.xsd
common/UBL-CommonBasicComponents-2.1.xsd
    → UBL-QualifiedDataTypes-2.1.xsd → UBL-UnqualifiedDataTypes-2.1.xsd
    → UBL-UnqualifiedDataTypes-2.1.xsd → CCTS_CCT_SchemaModule-2.1.xsd
```

Las rutas relativas se respetaron tal cual (`maindoc/` importa `../common/…`), de modo que el
esquema compila apuntando a los archivos locales y **no** sale a la red.

---

## 3. Compilación del esquema oficial

```python
from lxml import etree
doc = etree.parse(r"...\specs\contracts\ubl\oficial\maindoc\UBL-Invoice-2.1.xsd")
schema = etree.XMLSchema(doc)
```

**Resultado: COMPILA OK.**

| Comprobación | Resultado |
|---|---|
| `etree.XMLSchema(...)` sobre `UBL-Invoice-2.1.xsd` | Sin excepción |
| Entradas en `schema.error_log` | **0** |
| Raíz / targetNamespace | `schema` / `urn:oasis:names:specification:ubl:schema:xsd:Invoice-2` |
| `UBL-CreditNote-2.1.xsd` | Compila OK (0 errores) |
| `UBL-DebitNote-2.1.xsd` | Compila OK (0 errores) |

Que compile sin errores confirma además que las 16 dependencias están completas y bien
enlazadas: un solo `schemaLocation` roto habría hecho fallar la compilación.

---

## 4. Validación del ejemplo contra el esquema oficial

```python
schema = etree.XMLSchema(etree.parse(".../oficial/maindoc/UBL-Invoice-2.1.xsd"))
doc    = etree.parse(".../specs/contracts/ubl/ejemplo-invoice.xml")
schema.validate(doc)   # → True
```

**Resultado: el ejemplo ES VÁLIDO contra el esquema oficial de OASIS UBL 2.1.**

| Métrica | Valor |
|---|---|
| `schema.validate(...)` | **`True`** |
| Errores reportados | **0** |
| Líneas del XML señaladas | ninguna |
| Documento modificado | **No** (solo lectura; no se corrigió nada) |

### 4.1 Control negativo (prueba de que el validador realmente valida)

Un `True` solo es creíble si el validador es capaz de decir `False`. Se hicieron mutaciones
**en memoria** (el archivo del repositorio nunca se tocó):

| Mutación en memoria | Resultado | Mensaje |
|---|---|---|
| Añadir `cbc:ElementoInexistente` | `False` (1 error) | `This element is not expected. Expected is ( cac:InvoiceLine )` |
| Mover la primera `cac:InvoiceLine` antes de `cac:AccountingSupplierParty` | `False` (1 error, línea 95) | `Element 'cac:InvoiceLine': This element is not expected. Expected is one of ( cbc:BuyerReference, cac:InvoicePeriod, … )` |
| Eliminar `cbc:PayableAmount` de `cac:LegalMonetaryTotal` | `False` (1 error, línea 88) | `Missing child element(s). Expected is one of ( … cbc:PayableAmount )` |
| `cbc:IssueDate` = `22/10/2026` | `False` (1 error, línea 13) | `'22/10/2026' is not a valid value of the atomic type 'xs:date'` |

Conclusión del control: el esquema oficial está activo y detecta orden, cardinalidad y tipos.
El `True` del ejemplo es un resultado real, no un falso positivo.

---

## 5. Diferencias del ejemplo contra el esquema oficial

**Ninguna.** El XML de ejemplo no produce ni un solo error de validación contra
`UBL-Invoice-2.1.xsd`. Por tanto la lista numerada de diferencias (elemento / línea / qué espera
el esquema oficial) **queda vacía**: no hay elemento fuera de secuencia, ni cardinalidad
incumplida, ni tipo de dato mal formado, ni namespace incorrecto.

Lo que sí conviene dejar por escrito es el reverso de la moneda: **qué cosas el XSD oficial no
comprueba**. Eso se mide en el apartado 6 y es lo que justifica mantener el perfil propio.

---

## 6. Lo que el XSD oficial NO restringe (medido)

Estas **no son diferencias del ejemplo** (el ejemplo valida), sino **huecos de cobertura** del
esquema OASIS. Cada fila se comprobó mutando el XML en memoria y volviendo a validar contra el
esquema oficial. Sirven para saber qué debe seguir cubriendo el perfil propio y las reglas SUNAT.

| # | Elemento | Línea del XML | Mutación probada | ¿XSD oficial la acepta? | Qué sí espera / qué falta |
|---:|---|---:|---|---|---|
| 1 | `cbc:UBLVersionID` | 10 | `2.1` → `9.9` | **Sí** (sigue válido) | Solo tipo identificador; la versión `2.1` no está fijada en el XSD |
| 2 | `cbc:CustomizationID` | 11 | `2.0` → `cualquier-cosa` | **Sí** | Ningún valor obligatorio; el perfil SUNAT sí lo exige |
| 3 | `cbc:InvoiceTypeCode` | 15 | `01` → `99` | **Sí** | Código libre; no hay enumeración de tipos SUNAT |
| 4 | `cbc:DocumentCurrencyCode` | 17 | `PEN` → `XYZ` | **Sí** | No valida contra ISO 4217 (moneda inexistente aceptada) |
| 5 | `cbc:ID` con `schemeID` | 23 y 38 | `schemeID="6"` → `"ZZ"` | **Sí** | `schemeID` sin catálogo; no distingue RUC/DNI |
| 6 | `cbc:Note` | 16 | eliminar el nodo | **Sí** | Es `0..n`; el XSD no lo exige |
| 7 | `cbc:LineCountNumeric` | 18 | eliminar el nodo | **Sí** | `0..1`; no se contrasta con el nº real de líneas |
| 8 | `cbc:TaxInclusiveAmount` | 90 | eliminar el nodo | **Sí** | `0..1`; el total con impuestos no es obligatorio |
| 9 | `cbc:TaxableAmount` | 59 | `389.83` → `abc` | **No** (rechazado) | Sí valida el tipo decimal |
| 10 | `cbc:InvoicedQuantity` | 97 | `10` → `diez` | **No** (rechazado) | Sí valida el tipo decimal |
| 11 | Importes vs. aritmética | 57, 74, 89–91 | — | **No comprobable por XSD** | El XSD no suma líneas ni cuadra IGV/ICBPER contra los totales |
| 12 | `cbc:TaxExemptionReasonCode` | 112, 150, 188 | valores de texto libre | **Sí** | Catálogo no restringido |
| 13 | `cac:TaxTotal` duplicado | 56 y 73 | dos `TaxTotal` a nivel documento | **Sí** | `maxOccurs="unbounded"`; es legal |
| 14 | `cac:InvoiceLine` | 95 | eliminar todas las líneas | **No** (rechazado) | `1..n`; sí exige al menos una línea |

**Lectura:** el XSD oficial garantiza **estructura, orden, cardinalidad y tipos de dato**.
No garantiza **reglas de negocio**: cuadre de totales, catálogos SUNAT, RUC válido,
coherencia de `LineCountNumeric`, formato del nombre de archivo, etc. Eso vive en el perfil
propio y en las validaciones de negocio, no en OASIS.

### 6.1 Hallazgo colateral: atributo `schemaVersion` del perfil propio

El perfil `xsd/Invoice-2-profile.xsd` declara un atributo opcional en la raíz:

```xml
<xs:attribute name="schemaVersion" type="xs:string" use="optional"/>
```

Ese atributo **no existe en UBL 2.1**. Comprobado: un XML con `schemaVersion="2.1"` en `<Invoice>`
**pasa el perfil propio** pero **es rechazado por el esquema oficial**
(`Element '{…Invoice-2}Invoice': …`). El ejemplo actual **no usa** el atributo, por eso valida
sin problema; queda documentado como riesgo latente (si algún día se emite, el XML dejaría de
ser UBL-conforme). **No se ha corregido nada**: las reglas de la tarea prohíben tocar
`specs/contracts/ubl/xsd/`, así que solo se reporta.

---

## 7. Relación entre el esquema oficial y el perfil propio

El perfil propio se validó también (solo lectura) y **también acepta el ejemplo**. Para demostrar
que es un **subconjunto** del estándar y no un sustituto, se probaron elementos legales en UBL
pero ausentes del perfil (inserciones en la posición correcta de la secuencia):

| Prueba | Esquema oficial OASIS | Perfil propio |
|---|---|---|
| Ejemplo tal cual | **Válido** | **Válido** |
| `cbc:ProfileID` tras `cbc:CustomizationID` | Válido | **Inválido** (`This element is not expected`) |
| `cac:Delivery` antes de `cac:PaymentTerms` | Válido | **Inválido** |
| `cbc:CopyIndicator` = `false` tras `cbc:ID` | Válido | **Inválido** |
| Quitar `cbc:UBLVersionID` | Válido (`0..1`) | **Inválido** (el perfil lo exige) |
| Quitar `cbc:CustomizationID` | Válido (`0..1`) | **Inválido** (el perfil lo exige) |

Es decir: **casi todo lo que el perfil acepta es UBL válido, pero no todo UBL válido lo acepta el
perfil.** Eso es exactamente una restricción adicional (con la única excepción del atributo
`schemaVersion` descrita en 6.1, que es un caso de perfil *más laxo* que el estándar).

### 7.1 Diferencia de cobertura

| | Esquema oficial OASIS | Perfil propio local |
|---|---|---|
| Archivos | 16 (3 `maindoc` + 13 `common`) | 3 (`Invoice-2-profile.xsd` + 2 copias comunes) |
| Tamaño | 2 954 880 B (2.82 MB) | 11 832 B (~11.6 KB) |
| `CommonAggregateComponents` | 2 804 elementos declarados | 48 elementos declarados |
| `CommonBasicComponents` | 873 elementos declarados | 25 elementos declarados |
| Cobertura | Estándar completo UBL 2.1 | Solo los campos del perfil SUNAT del proyecto |

El perfil usa **copias reducidas propias** de los componentes comunes
(`xsd/CommonBasicComponents-2.xsd`, 3 481 B; `xsd/CommonAggregateComponents-2.xsd`, 6 002 B),
no los oficiales. Por eso no puede demostrar conformidad con UBL 2.1: demuestra conformidad con
*el perfil del proyecto*.

### 7.2 Recomendación de uso (sin cambiar nada en este trabajo)

Validar en dos pasos, ambos obligatorios:

1. **Conformidad UBL 2.1** — contra `oficial/maindoc/UBL-Invoice-2.1.xsd` (esquema oficial OASIS).
   Es la prueba que exige el estándar y la que se puede mostrar al profesor / a un tercero.
2. **Restricción de perfil SUNAT** — contra `xsd/Invoice-2-profile.xsd`. Añade los campos
   obligatorios y el subconjunto permitido del proyecto.

El paso 1 no se puede sustituir por el paso 2 (el paso 2 es más débil en cobertura del estándar):
un XML puede pasar el perfil y no ser UBL válido, como demuestra `schemaVersion` en 6.1.

---

## 8. Reproducibilidad

Todo se ejecutó con el Python 3.13 indicado y `PYTHONPATH=C:\Users\benny\Desktop\Arquitectura\_tools`.
No se usó `git` ni `pip`. Los scripts se pasaron por *stdin* (`python -`), de modo que **no se creó
ningún archivo fuera de `specs/contracts/ubl/oficial/` ni del presente informe**.

Descarga recursiva (esquema + cierre de dependencias):

```powershell
$py = "C:\Users\benny\AppData\Local\Programs\Python\Python313\python.exe"
$env:PYTHONPATH = "C:\Users\benny\Desktop\Arquitectura\_tools"
# se recorre cada xsd:import/xsd:include, se resuelve schemaLocation con urljoin
# y se guarda respetando la ruta relativa bajo specs/contracts/ubl/oficial/
$code | & $py -
```

Compilación y validación:

```python
import os
from lxml import etree
BASE = r"C:\Users\benny\Desktop\Arquitectura\Medio curso Arquitectura 2026-II\specs\contracts\ubl"
schema = etree.XMLSchema(etree.parse(os.path.join(BASE, "oficial", "maindoc", "UBL-Invoice-2.1.xsd")))
print(schema.error_log)                                            # 0 entradas
print(schema.validate(etree.parse(os.path.join(BASE, "ejemplo-invoice.xml"))))   # True
print(len(schema.error_log))                                       # 0
```

---

## 9. Limitaciones y lo que NO se comprobó

Para no dar por cierto lo que no se midió:

- **No se validó contra los esquemas de SUNAT**: no estaban en el alcance de esta tarea; aquí solo
  se usan los oficiales de OASIS. La conformidad UBL 2.1 **no equivale** a aceptación por SUNAT.
- **No se validó criptográficamente la firma**: los esquemas de XMLDSig/XAdES se descargaron y
  compilan, pero el ejemplo no lleva firma y el XSD no verifica firmas, solo su estructura.
- **`CreditNote` y `DebitNote`**: se descargaron y compilan, pero **no se validaron instancias**
  contra ellos (no hay XML de nota de crédito/débito en el alcance).
- **Reglas de negocio**: no evaluadas (cuadre de totales, RUC módulo 11, catálogos SUNAT).
  El XSD no las cubre (apartado 6).
- **Sin cambios en el repositorio**: no se editó `ejemplo-invoice.xml`, ni `xsd/`,
  ni `validacion/`, ni `docs/`, ni `src/`, ni `tests/`.
- **Fecha de los archivos en el servidor**: los `Last-Modified` devueltos por el CDN son
  `Sun, 05 Apr 2026`, que es la fecha de publicación en el CDN y no la del release; la fecha
  real del estándar es la que declara la cabecera de cada XSD (*04 November 2013*).

---

## 10. Conclusión

- Los **16 esquemas oficiales** de OASIS UBL 2.1 están descargados, verificados e íntegros en
  `specs/contracts/ubl/oficial/`, con la estructura `maindoc/` + `../common/` que exigen sus imports.
- El esquema oficial **compila sin errores** con lxml 6.1.3.
- El ejemplo `ejemplo-invoice.xml` **valida contra el esquema oficial: 0 errores**. Es decir,
  **el XML del proyecto ya es conforme a UBL 2.1**; no hay nada que corregir en él.
- Por tanto, **no hay diferencias que listar** contra el esquema oficial. Lo que el XSD oficial
  no cubre (catálogos SUNAT, cuadre de importes, versión, tipos de documento) es precisamente
  el trabajo del **perfil propio**, que actúa como **restricción adicional** y **no como sustituto**
  del estándar.
