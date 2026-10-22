# Esqueleto de Especificaciones Técnicas — Facturación Electrónica

**Universidad Nacional Agraria de la Selva**
Facultad de Ingeniería en Informática y Sistemas
**Curso:** Arquitectura de Software — Examen de Medio Curso, Grupo "A"
**Fecha del examen:** 19 de octubre de 2026 · **Duración:** 2:00 horas
**Alumno:** ______________________________________  **Docente:** ______________________

---

**Cliente del caso:** ABC Software Corp
**Entregable:** Primera fase (**Spec-First**) — esqueleto de especificaciones técnicas
**Fecha de entrega:** 22 de octubre de 2026
**Equipo:** Arquitectura de Software

> **Versión para imprimir o entregar:** [`MEMORIA-TECNICA.docx`](MEMORIA-TECNICA.docx) — el mismo
> contenido consolidado en un documento con portada, figuras y evidencias.

---

## 1. Qué se entrega

El examen enumera cuatro artefactos. Esta entrega los cubre uno a uno, con la misma denominación:

| # | Entregable exigido por el examen | Dónde está | Evidencia |
|---|---|---|---|
| **E1** | *El Modelo de Dominio y Contratos (DTOs / Schemas)* | [`specs/domain/modelo-dominio.md`](specs/domain/modelo-dominio.md) · [diagrama de clases](docs/arquitectura/07-diagrama-clases.md) · [`specs/contracts/dto/`](specs/contracts/dto/) | 7 JSON Schemas (petición y respuesta) validados por script |
| **E2** | *Diagramas de Arquitectura MVC con visión a Hexagonal* | [`specs/architecture/mvc-hexagonal.md`](specs/architecture/mvc-hexagonal.md) · [`docs/arquitectura/`](docs/arquitectura/README.md) | 11 requisitos ASR + 2 diagramas SVG + tabla de equivalencia |
| **E3** | *Especificación de Endpoints / Servicios (Contratos API)* | [`specs/contracts/facturacion-api.yaml`](specs/contracts/facturacion-api.yaml) | 9 rutas, 15 referencias resueltas, seguridad y catálogo de errores |
| **E4** | *Matriz de Trazabilidad Normativa con cruces entre datos SUNAT y datos UBL* | [`docs/arquitectura/04-matriz-trazabilidad-normativa.md`](docs/arquitectura/04-matriz-trazabilidad-normativa.md) | 59 cruces, 9 catálogos, 24 reglas |

## 2. Cómo leerlo (orden sugerido)

```text
1. Este resumen
2. 00-caso.md                       ← qué pidió el examen y qué requisitos se derivaron
3. specs/domain/modelo-dominio.md   ← las entidades y sus reglas
4. specs/domain/reglas-negocio.md   ← las 24 reglas numeradas (RN-01..RN-24)
5. docs/arquitectura/README.md      ← los dos diagramas y el plan de migración
6. specs/contracts/facturacion-api.yaml  ← el contrato de servicios
7. docs/arquitectura/04-matriz...   ← el cruce normativo (el corazón de la entrega)
8. docs/arquitectura/05 y 06        ← migración del legado y empaquetado MSI/APK
9. specs/adr/                       ← las decisiones y por qué
10. src/puertos.py · tests/         ← el borde dejado listo para la fase 2
```

## 3. Decisiones de arquitectura (resumen)

| Decisión | Por qué | Consecuencia |
|---|---|---|
| **Monolito MVC con fronteras ya dibujadas** | la gerencia pide MVC hoy y hexagonal mañana | migrar es cambiar implementaciones, no reescribir reglas |
| **Dominio sin dependencias de framework** | las reglas tributarias son el activo del negocio | se prueban sin servidor ni base de datos |
| **Un perfil UBL propio, validado contra XSD** | SUNAT rechaza XML inválido | el error se detecta antes de enviar |
| **Los totales se calculan, nunca se reciben** | el cliente no debe poder manipular importes | IGV/ISC/ICBPER siempre coherentes |
| **El certificado digital vive en el servidor** | un certificado en el móvil se puede extraer | la app Android no firma, solo solicita |
| **Migración con trazabilidad total** | el legado es la única historia de la empresa | ninguna ficha se descarta en silencio |

## 4. Evidencia de que los contratos están vivos

Los contratos no son documentos muertos: hay dos validadores que los ejecutan.

```bash
python validacion/validar_contratos.py    # DTOs, OpenAPI y ejemplos
python validacion/validar_xml_ubl.py      # XML del perfil contra su XSD
```

Resultado obtenido:

```text
validar_contratos.py → 13 comprobaciones correctas, 0 fallos
  OK  7 esquemas JSON válidos (petición y respuesta)
  OK  el ejemplo válido cumple su esquema
  OK  el ejemplo inválido se rechaza con 4 errores
  OK  el ejemplo de respuesta cumple comprobante-response
  OK  OpenAPI: estructura mínima presente
  OK  OpenAPI: 15 referencias a esquemas, todas resueltas
  OK  OpenAPI: 9 rutas declaradas

validar_xml_ubl.py → 6 comprobaciones correctas, 0 fallos
  OK  ejemplo-invoice.xml valida contra Invoice-2-profile.xsd
  OK  un XML sin cbc:ID es rechazado por el XSD
  OK  suma de líneas = 449.83 coincide con el total
  OK  TaxInclusiveAmount = 530.00 incluye IGV e ICBPER
  OK  PayableAmount = 530.00 coincide con el total con impuestos
  OK  una cantidad negativa pasa el XSD pero la rechaza RN-14
```

## 5. Cumplimiento de las restricciones del caso

| Restricción del examen | Cómo se cumple | Archivo |
|---|---|---|
| Migración del legado sin perder trazabilidad | mapeo campo a campo + estado `OBSERVADA` con motivo | [`docs/arquitectura/05`](docs/arquitectura/05-migracion-legado.md) |
| Normativa tributaria peruana | 24 reglas + 9 catálogos + matriz de 59 cruces | [`docs/arquitectura/04`](docs/arquitectura/04-matriz-trazabilidad-normativa.md) |
| **Normas citadas (RS 097-2012, RS 234-2006)** | qué regula cada norma y dónde se implementa | [`marco-normativo`](specs/domain/marco-normativo.md) |
| Catálogo 8 como punto clave | tabla completa + reglas de combinación por comprobante | [`catalogs`](specs/contracts/catalogs/catalogos-sunat.md) |
| Monolito MVC con visión hexagonal **en los specs** | 11 requisitos ASR verificables + 2 diagramas + plan de migración | [`specs/architecture`](specs/architecture/mvc-hexagonal.md) |
| Windows y Android | decisión de stack (ADR-0003) + MSI/APK + consecuencias | [`docs/arquitectura/06`](docs/arquitectura/06-distribucion-msi-apk.md) |
| Casos de uso detallados | 10 casos + 10 escenarios Gherkin + benchmark de usuarios | [`features`](specs/features/casos-de-uso.md) · [`benchmark`](docs/benchmark-facturacion.md) |
| Estudio del `UBL-Invoice-2.1.xsd` | extracto del esquema, enlace OASIS y derivación del perfil | [`perfil`](specs/contracts/ubl/perfil-invoice.md), sección 7 |

## 6. Alcance de esta fase (y por qué aún no hay lógica implementada)

El enunciado **no prohíbe codificar**: exige **no codificar sin especificar antes** — *"primero
definir las reglas, contratos de datos, validaciones y contratos de interfaz antes de escribir una
sola línea de lógica de negocio"*. Esta entrega es la **primera fase**: deja el borde trazado para
que la fase 2 escriba código sin reinterpretar el negocio.

| Ya definido en esta fase | Se implementa en la fase 2 |
|---|---|
| Puertos e interfaces (`src/puertos.py`) | Controladores, servicios de dominio y adaptadores |
| Reglas RN-01..RN-24 | Cálculo ejecutable de IGV, ISC e ICBPER |
| Contrato OpenAPI + DTOs (JSON Schema) | Endpoints funcionando contra el contrato |
| Mock (`tests/mocks/mock_db.py`) y mapa de pruebas | Tests ejecutados contra la aplicación |
| Flujo de firma, validación XSD y envío | Firma XMLDSig real y cliente OSE |
| Arquitectura MVC y plan de migración | Empaquetado MSI/APK |

**Fuera de alcance total** (declarado): certificación como emisor electrónico ante SUNAT, resumen
diario de boletas y comunicación masiva de bajas.

## 7. Riesgos identificados

| Riesgo | Impacto | Mitigación propuesta |
|---|---|---|
| Catálogos SUNAT cambian | comprobantes rechazados | catálogos como datos, no como código |
| Productos del legado mal escritos | migración con observadas | proceso de normalización y revisión con almacén |
| Certificado digital mal resguardado | suplantación tributaria | el certificado nunca sale del servidor |
| Crecimiento a microservicios prematuro | sobrecosto | el dominio ya está aislado: se espera el volumen |
