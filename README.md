# Facturación Electrónica — ABC Software Corp

Primera fase (**Spec-First**) del sistema de facturación electrónica del caso de examen de
Arquitectura de Software: **reglas, contratos, validaciones y arquitectura definidos antes de la
primera línea de negocio**.

> **Regla que ordena todo el diseño:** sin XML válido y firmado no existe comprobante. Ningún
> comprobante se marca como emitido si no pasó la validación formal y el CDR.

## Trazabilidad al enunciado (frase del examen → dónde está)

| El examen pide… | Dónde está | Estado |
|---|---|---|
| *"El Modelo de Dominio y Contratos (DTOs / Schemas)"* | [specs/domain](specs/domain/modelo-dominio.md) · [specs/contracts/dto](specs/contracts/dto/) | ✅ |
| *"Diagramas de Arquitectura MVC con visión a Hexagonal"* | [specs/architecture](specs/architecture/mvc-hexagonal.md) · [docs/arquitectura](docs/arquitectura/README.md) | ✅ |
| *"Especificación de Endpoints / Servicios (Contratos API)"* | [facturacion-api.yaml](specs/contracts/facturacion-api.yaml) | ✅ |
| *"Matriz de Trazabilidad Normativa con cruces entre datos SUNAT y datos UBL"* | [04-matriz](docs/arquitectura/04-matriz-trazabilidad-normativa.md) · [08-tabla de match](docs/arquitectura/08-tabla-match-sunat-ubl.md) | ✅ |
| *"Legado y Migración de Datos … sin perder trazabilidad"* | [05-migracion-legado](docs/arquitectura/05-migracion-legado.md) · RN-21..RN-24 | ✅ |
| *"Normativa Tributaria Peruana … el catálogo 8 de SUNAT"* | [catalogos](specs/contracts/catalogs/catalogos-sunat.md) · [marco normativo](specs/domain/marco-normativo.md) | ✅ |
| *"monolítica limpia … MVC … Arquitectura Hexagonal o Clean Architecture"* | [mvc-hexagonal](specs/architecture/mvc-hexagonal.md) · [ADR-0001](specs/adr/0001-monolito-mvc-con-vision-hexagonal.md) | ✅ |
| *"Windows … Android … instalador MSI … APK"* | [06-distribucion](docs/arquitectura/06-distribucion-msi-apk.md) · [ADR-0003](specs/adr/0003-estrategia-multiplataforma.md) | ✅ |
| *"detalle los casos posibles … Nubefact"* | [casos de uso](specs/features/casos-de-uso.md) · [benchmark](docs/benchmark-facturacion.md) | ✅ |

---

## Índice

| Documento | Contenido |
|---|---|
| **[MEMORIA-TECNICA.docx](MEMORIA-TECNICA.docx)** | **Documento consolidado para entregar/imprimir** (portada, figuras y evidencias) |
| [VERIFICACION.md](VERIFICACION.md) | **Informe de verificación**: enunciado → evidencia, pruebas y límites |
| [01-RESUMEN-EJECUTIVO.md](01-RESUMEN-EJECUTIVO.md) | **Empieza aquí**: qué se entrega y cómo se lee |
| [00-caso.md](00-caso.md) | Transcripción del examen + requisitos REQ-01..REQ-12 |
| [specs/domain/modelo-dominio.md](specs/domain/modelo-dominio.md) | **E1** — entidades, invariantes, DTOs |
| [specs/domain/reglas-negocio.md](specs/domain/reglas-negocio.md) | **E1** — 24 reglas (impuestos, numeración, migración) |
| [specs/domain/marco-normativo.md](specs/domain/marco-normativo.md) | Normas citadas (RS 097-2012, RS 234-2006) y su trazabilidad |
| [specs/architecture/mvc-hexagonal.md](specs/architecture/mvc-hexagonal.md) | **E2** — 11 requisitos ASR de MVC → Hexagonal |
| [specs/contracts/facturacion-api.yaml](specs/contracts/facturacion-api.yaml) | **E3** — contrato OpenAPI (9 rutas) |
| [specs/contracts/dto/](specs/contracts/dto/) | **E1** — 7 JSON Schemas + ejemplo válido e inválido |
| [specs/contracts/catalogs/catalogos-sunat.md](specs/contracts/catalogs/catalogos-sunat.md) | Catálogos 01, 02, 03, 05, 07, **08**, 09, 10, 51 |
| [specs/contracts/ubl/perfil-invoice.md](specs/contracts/ubl/perfil-invoice.md) | Perfil UBL 2.1 Invoice con rutas y orden |
| [specs/features/casos-de-uso.md](specs/features/casos-de-uso.md) | 10 casos de uso + 10 escenarios Gherkin |
| [docs/arquitectura/README.md](docs/arquitectura/README.md) | **E2** — diagramas MVC y hexagonal |
| [docs/arquitectura/04-matriz-trazabilidad-normativa.md](docs/arquitectura/04-matriz-trazabilidad-normativa.md) | **E4** — 59 cruces SUNAT ↔ UBL |
| [docs/arquitectura/08-tabla-match-sunat-ubl.md](docs/arquitectura/08-tabla-match-sunat-ubl.md) | **Tabla de match**: campo SUNAT (`serie_numero`, …) ↔ UBL ↔ DTO |
| [docs/arquitectura/05-migracion-legado.md](docs/arquitectura/05-migracion-legado.md) | Migración de fichas con trazabilidad |
| [docs/arquitectura/06-distribucion-msi-apk.md](docs/arquitectura/06-distribucion-msi-apk.md) | Windows (MSI) y Android (APK) |
| [docs/arquitectura/07-diagrama-clases.md](docs/arquitectura/07-diagrama-clases.md) | **E1** — diagrama de clases del dominio |
| [docs/benchmark-facturacion.md](docs/benchmark-facturacion.md) | Dolores de usuarios → decisiones de diseño |
| [specs/adr/](specs/adr/) | 3 decisiones de arquitectura justificadas |
| [src/puertos.py](src/puertos.py) | Interfaces del dominio (el borde para la fase 2) |
| [tests/mocks/mock_db.py](tests/mocks/mock_db.py) | Datos estáticos que simulan la persistencia |
| [validacion/validar_contratos.py](validacion/validar_contratos.py) | Valida los contratos (sin dependencias) |

## Verificar la entrega

```bash
pip install -r requirements.txt
python validacion/verificar_entrega.py     # todo en un comando: 7 comprobaciones
```

Salida esperada: **7/7 comprobaciones correctas**, código de salida `0`.

El script ejecuta los otros dos validadores y añade integridad del repositorio:

```bash
python validacion/validar_contratos.py     # 13 comprobaciones (schemas + OpenAPI)
python validacion/validar_xml_ubl.py       # 6 comprobaciones (XML contra XSD)
```

## Estructura (alineada al molde de clase)

```text
examen/
├── .editorconfig
├── .gitignore
├── README.md
├── MEMORIA-TECNICA.docx                documento consolidado (portada + figuras)
├── 00-caso.md                          caso transcrito + requisitos
├── 01-RESUMEN-EJECUTIVO.md             portada de la entrega
├── docs/
│   ├── SDD_WORKFLOW.md                 ciclo Spec-First (5 etapas)
│   ├── benchmark-facturacion.md        dolores de usuarios → decisiones de diseño
│   └── arquitectura/
│       ├── README.md                   E2 — lectura de los diagramas
│       ├── 01-mvc-capas.svg
│       ├── 02-hexagonal.svg
│       ├── 03-secuencia-emision.md
│       ├── 04-matriz-trazabilidad-normativa.md   E4
│       ├── 05-migracion-legado.md
│       ├── 06-distribucion-msi-apk.md
│       ├── 07-diagrama-clases.md + .svg          E1
│       └── 08-tabla-match-sunat-ubl.md           match por campo SUNAT
├── specs/
│   ├── README.md                       reglas de la carpeta
│   ├── adr/                            0001 MVC→Hexagonal · 0002 UBL/XSD · 0003 multiplataforma
│   ├── architecture/                   mvc-hexagonal (requisitos ASR)
│   ├── contracts/                      OpenAPI + dto/ + catalogs/ + ubl/
│   ├── domain/                         modelo-dominio · reglas-negocio · marco-normativo
│   ├── features/                       casos-de-uso (Gherkin)
│   └── templates/                      plantillas de spec, ADR y contrato
├── src/
│   ├── puertos.py                      interfaces (fase 1: sin lógica)
│   └── README.md                       estructura MVC de la fase 2
├── tests/
│   ├── README.md                       mapa de pruebas por nivel
│   ├── acceptance/  integration/  unit/
│   └── mocks/mock_db.py                datos estáticos del dominio
└── validacion/
    ├── verificar_entrega.py           8 comprobaciones (todo en uno)
    ├── validar_contratos.py           esquemas + OpenAPI
    └── validar_xml_ubl.py             XML contra XSD
```

## Alcance: qué es esta fase y qué sigue

El enunciado pide **no codificar sin especificar**: definir reglas, contratos y validaciones antes de
la primera línea de negocio. Por eso esta entrega incluye:

| Sí incluye | No incluye (fase 2) |
|---|---|
| Contratos, DTOs y catálogos | Implementación de los endpoints |
| Reglas de negocio numeradas | Cálculo ejecutable de IGV/ISC/ICBPER |
| Diagramas MVC y hexagonal | Código de controladores y adaptadores |
| Puertos (interfaces) en `src/` | Implementación de esos puertos |
| Mock y mapa de pruebas | Tests ejecutados contra la app |
| Matriz de trazabilidad y tabla de match | Integración real con OSE/SUNAT |
| **Nada de interfaz de usuario** | Pantallas, wireframes o prototipos |

> El alcance es **especificación técnica**: no se diseña interfaz de usuario. El contrato API es un
> contrato de servicio, no una pantalla; la restricción MSI/APK se documenta, no se prototipa.

El borde ya está definido: la fase 2 implementa lo que aquí se especificó, sin cambiar los contratos.
