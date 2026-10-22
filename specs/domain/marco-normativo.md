# Marco normativo — SUNAT, UBL y reglas de emisión

**Origen:** el caso cita expresamente la **RS N° 097-2012**, la **RS N° 234-2006** y *"las normativas
modernas de masificación de comprobantes electrónicos"*, y exige *"estricto cumplimiento de los
requisitos de la SUNAT"*.

Este documento explica **qué norma hay detrás de cada regla** del sistema. No transcribe artículos: los
mapea.

> **Advertencia de vigencia:** el texto de las resoluciones cambia con frecuencia (nuevas
> resoluciones modifican catálogos y plazos). Antes de implementar en producción debe verificarse la
> versión vigente en el portal de SUNAT. Lo que aquí se fija es **qué regla del sistema** se deriva de
> cada bloque normativo.

---

## 1. Normas citadas por el caso

| Norma | Qué regula (según el caso y el marco del SEE) | Dónde se implementa |
|---|---|---|
| **RS N° 097-2012/SUNAT** | Régimen del **Sistema de Emisión Electrónica (SEE)**: obligación de emitir comprobantes electrónicos y su validación | Catálogos + reglas de emisión (RN-10..RN-13) |
| **RS N° 234-2006/SUNAT** | Antecedente del SEE para la emisión electrónica de comprobantes | Requisito de estructura UBL y firma (ADR-0002) |
| **Normativa moderna de masificación de CPE** | Obligatoriedad progresiva de emitir comprobantes de pago electrónicos; designación como emisor electrónico | Estado `EMITIDO`/`ACEPTADO`, CDR (RN-17, RN-19) |
| **UBL 2.1 (OASIS)** | Estructura del documento `Invoice` / `DispatchAdvice` | [`perfil-invoice.md`](../contracts/ubl/perfil-invoice.md) |

## 2. Estándar técnico: UBL 2.1

| Aspecto | Definición | Artefacto |
|---|---|---|
| Especificación | OASIS — Universal Business Language 2.1 | [docs.oasis-open.org/ubl/os-UBL-2.1](https://docs.oasis-open.org/ubl/os-UBL-2.1/) |
| Esquema | `UBL-Invoice-2.1.xsd` (documento principal) + `CommonBasicComponents` + `CommonAggregateComponents` | [`perfil-invoice.md`](../contracts/ubl/perfil-invoice.md) |
| Namespaces | `Invoice-2`, `CommonAggregateComponents-2`, `CommonBasicComponents-2` | perfil, sección 1 |
| Validación | XSD obligatorio antes del envío | RN-18 |

## 3. Catálogos exigidos por el caso

El enunciado nombra cuatro explícitamente y señala uno como **punto clave**:

| Catálogo | Contenido | Dónde |
|---|---|---|
| Tipos de documentos | código 01, 03, 07, 08 | [`catalogs/catalogos-sunat.md`](../contracts/catalogs/catalogos-sunat.md) |
| Afectación al IGV | códigos 10, 20, 30, 40 y familia | mismo archivo |
| Códigos de moneda | PEN, USD | mismo archivo |
| **Catálogo 8** ★ | **tipo de documento de identidad** del receptor | mismo archivo, sección dedicada |
| Otros usados | 03 unidad de medida, 05 tributo, 09/10 notas, 51 tipo de operación | mismo archivo |

## 4. Reglas de emisión que se derivan

| Bloque normativo | Regla del sistema | Verificación |
|---|---|---|
| Series y correlativos | RN-10, RN-11, RN-12 | unicidad por `tipo+serie`; formato `F001-00000001` |
| Fecha y hora de emisión | RN-13 | no futura; `HH:mm:ss` |
| Validación de RUC | RN-01 | módulo 11 |
| Documento del receptor | RN-02 | catálogo 8 + combinación por comprobante |
| Cálculo de tributos | RN-04..RN-09 | IGV 18%, ISC, ICBPER S/ 0.50 |
| Inmutabilidad | RN-15 | corrección solo por nota |
| Notas de crédito/débito | RN-16 | referencia + catálogo 09/10 |
| Firma y envío | RN-18, RN-19, RN-20 | XMLDSig + XSD + CDR |

## 5. Impuestos: qué se aplica y qué no

| Tributo | Regla | Observación |
|---|---|---|
| **IGV** | 18% sobre operaciones gravadas (códigos 10–17) | exonerado (20), inafecto (30) y exportación (40) no generan IGV |
| **ISC** | tasa por producto sobre el valor de venta | solo productos afectos (combustibles, licores, etc.) |
| **ICBPER** | **S/ 0.50 por bolsa plástica** | monto fijo, no porcentaje; no forma parte de la base del IGV |

> **Nota de precisión:** el tributo se denomina **ICBPER** (Impuesto al Consumo de Bolsas de
> Plástico). Se usa la sigla oficial en todo el diseño.

## 6. Emisión electrónica: dos caminos

| Camino | Descripción | Consecuencia en el diseño |
|---|---|---|
| **A través de una OSE** | un Operador de Servicios Electrónicos recibe el XML y lo presenta a SUNAT | el sistema depende de un `ISunatGateway` externo |
| **Directo a SUNAT** | el emisor envía por el SEE usando su certificado | mismo puerto, distinto adaptador |

El diseño **no decide** por uno: la interfaz `ISunatGateway` permite ambos. El certificado digital
vive siempre en el servidor (ADR-0002).

## 7. Requisitos que el emisor debe cumplir (contexto)

| Requisito | Estado en el diseño |
|---|---|
| RUC activo y habido | validación RN-01 |
| Certificado digital vigente | declarado; su gestión es operativa (no de esta fase) |
| Designación como emisor electrónico | proceso administrativo del cliente, fuera del sistema |
| Series registradas | RN-10 (formato) + validación de existencia (fase 2) |
| Conservación de XML y CDR | el comprobante guarda ambos (RN-19) |

## 8. Trazabilidad norma → regla → entrega

| Norma | Regla | Entregable que la evidencia |
|---|---|---|
| RS 097-2012 / masificación CPE | RN-17, RN-19 | máquina de estados + CDR (E1, E4) |
| UBL 2.1 (OASIS) | RN-18 | perfil + matriz (E1, E4) |
| Catálogo 8 | RN-02 | catálogos + matriz filas 19-20 (E1, E4) |
| Catálogos 01/02/03/05/07/51 | RN-04..RN-12 | catálogos + contrato (E1, E3) |
| Reglas de emisión | RN-10..RN-13 | contrato + reglas (E1, E3) |

## 9. Riesgos normativos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Cambio de catálogos | datos históricos inconsistentes | catálogos como **datos versionados**, no como constantes en código |
| Nueva resolución que cambia plazos | rechazos | parámetros de configuración, no valores fijos |
| SUNAT migra de versión de UBL | XML inválido | el perfil está aislado en un solo artefacto |
| Certificado vencido | no se puede emitir | alerta de vencimiento (fase 2) |
