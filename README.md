<div align="center">

# Facturación Electrónica — ABC Software Corp

**Esqueleto de especificaciones técnicas** · Fase 1 del ciclo **Spec-First**

![Fase](https://img.shields.io/badge/fase-1%20%C2%B7%20especificaci%C3%B3n-1F3A5F)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.3-6BA539)
![UBL](https://img.shields.io/badge/UBL-2.1-orange)
![Verificación](https://img.shields.io/badge/verificaci%C3%B3n-15%20%2B%2011%20%2B%208-brightgreen)

*Arquitectura de Software · Universidad Nacional Agraria de la Selva · Examen de Medio Curso · Grupo "A"*

</div>

> [!IMPORTANT]
> **Regla que ordena todo el diseño:** sin XML válido y firmado no existe comprobante. Ningún
> comprobante se marca como emitido si no pasó la validación formal y el CDR.

Este repositorio contiene la **primera fase** del proyecto: las reglas, contratos, validaciones y
arquitectura definidos **antes** de escribir una línea de lógica de negocio. No incluye interfaz de
usuario ni implementación; incluye lo que hace posible implementarlas sin reinterpretar el negocio.

---

## Entregables

| # | Entregable del enunciado | Dónde está | Evidencia |
|:--:|---|---|---|
| **E1** | Modelo de Dominio y Contratos (DTOs / Schemas) | [`specs/domain/`](specs/domain/modelo-dominio.md) · [`specs/contracts/dto/`](specs/contracts/dto/) | 7 JSON Schemas validados |
| **E2** | Diagramas de Arquitectura MVC con visión a Hexagonal | [`specs/architecture/`](specs/architecture/mvc-hexagonal.md) · [`docs/arquitectura/`](docs/arquitectura/README.md) | 11 requisitos ASR + 10 RNF + 3 ADR |
| **E3** | Especificación de Endpoints / Servicios (Contratos API) | [`facturacion-api.yaml`](specs/contracts/facturacion-api.yaml) | 9 rutas · 15 esquemas · JWT |
| **E4** | Matriz de Trazabilidad Normativa SUNAT ↔ UBL | [`04-matriz`](docs/arquitectura/04-matriz-trazabilidad-normativa.md) · [`08-tabla de match`](docs/arquitectura/08-tabla-match-sunat-ubl.md) | 59 cruces + 47 campos |

📄 **Documento consolidado para entregar:** [`MEMORIA-TECNICA.docx`](MEMORIA-TECNICA.docx) ·
🔍 **Informe de verificación:** [`VERIFICACION.md`](VERIFICACION.md)

---

## Cómo se ve la arquitectura

<div align="center">

<img src="docs/arquitectura/01-mvc-capas.svg" width="49%" alt="Arquitectura MVC en capas">
<img src="docs/arquitectura/02-hexagonal.svg" width="49%" alt="Visión hexagonal: puertos y adaptadores">

*Izquierda: monolito MVC de hoy · Derecha: visión objetivo con puertos y adaptadores*

<img src="docs/arquitectura/07-diagrama-clases.svg" width="72%" alt="Diagrama de clases del dominio">

*Modelo de dominio: `Comprobante` es la raíz de agregado; `Totales`, `Cdr` y `Cuota` son objetos de valor*

</div>

---

## Verificación

Los contratos no son documentos muertos: hay tres validadores ejecutables.

```bash
pip install -r requirements.txt
python validacion/verificar_entrega.py     # todo en uno
```

| Script | Qué comprueba | Resultado |
|---|---|---|
| [`verificar_entrega.py`](validacion/verificar_entrega.py) | integral: contratos, XML, enlaces, cifras, artefactos | **8/8** |
| [`validar_contratos.py`](validacion/validar_contratos.py) | 7 JSON Schemas, 3 ejemplos y el OpenAPI (parseo real) | **15/15** |
| [`validar_xml_ubl.py`](validacion/validar_xml_ubl.py) | XML contra XSD, totales, RUC (módulo 11) | **11/11** |

Incluyen **controles negativos** que demuestran que las pruebas sirven: quitar `serie_numero` del
ejemplo rompe la validación (código de salida 1); adulterar el IGV de cabecera rompe la reconciliación
de totales.

---

## Estructura

<details>
<summary><b>Ver el árbol completo del repositorio</b></summary>

```text
examen/
├── MEMORIA-TECNICA.docx          documento consolidado (portada + figuras)
├── VERIFICACION.md               informe: enunciado → evidencia → pruebas
├── 00-caso.md                    caso transcrito + requisitos REQ-01..REQ-12
├── 01-RESUMEN-EJECUTIVO.md       portada y mapa de entregables
├── docs/
│   ├── SDD_WORKFLOW.md           ciclo Spec-First
│   ├── benchmark-facturacion.md  dolores de usuarios → decisiones
│   └── arquitectura/
│       ├── README.md             lectura de los diagramas
│       ├── 01-mvc-capas.svg/.png
│       ├── 02-hexagonal.svg/.png
│       ├── 03-secuencia-emision.md
│       ├── 04-matriz-trazabilidad-normativa.md    E4
│       ├── 05-migracion-legado.md
│       ├── 06-distribucion-msi-apk.md
│       ├── 07-diagrama-clases.svg/.png            E1
│       └── 08-tabla-match-sunat-ubl.md            match por campo
├── specs/
│   ├── README.md                 reglas de la carpeta
│   ├── adr/                      0001 MVC→Hexagonal · 0002 UBL/XSD · 0003 multiplataforma
│   ├── architecture/             mvc-hexagonal (ASR + RNF)
│   ├── contracts/                OpenAPI + dto/ + catalogs/ + ubl/ (con XSD)
│   ├── domain/                   modelo-dominio · reglas-negocio · marco-normativo
│   ├── features/                 casos de uso (Gherkin)
│   └── templates/                plantillas de spec, ADR y contrato
├── src/                          puertos (interfaces) + README de la fase 2
├── tests/                        mapa de pruebas + mock de datos
└── validacion/                   los tres validadores
```

</details>

---

## Trazabilidad al enunciado

<details>
<summary><b>Ver cada exigencia del examen y dónde se cubre</b></summary>

| El examen pide… | Dónde está |
|---|---|
| *"El Modelo de Dominio y Contratos (DTOs / Schemas)"* | [`specs/domain`](specs/domain/modelo-dominio.md) · [`specs/contracts/dto`](specs/contracts/dto/) |
| *"Diagramas de Arquitectura MVC con visión a Hexagonal"* | [`specs/architecture`](specs/architecture/mvc-hexagonal.md) · [`docs/arquitectura`](docs/arquitectura/README.md) |
| *"Especificación de Endpoints / Servicios (Contratos API)"* | [`facturacion-api.yaml`](specs/contracts/facturacion-api.yaml) |
| *"Matriz de Trazabilidad Normativa con cruces entre datos SUNAT y datos UBL"* | [`04-matriz`](docs/arquitectura/04-matriz-trazabilidad-normativa.md) · [`08-tabla de match`](docs/arquitectura/08-tabla-match-sunat-ubl.md) |
| *"Legado y Migración de Datos … sin perder trazabilidad"* | [`05-migracion`](docs/arquitectura/05-migracion-legado.md) · RN-21..RN-24 |
| *"Normativa Tributaria Peruana … el catálogo 8 de SUNAT"* | [`catalogos`](specs/contracts/catalogs/catalogos-sunat.md) · [`marco normativo`](specs/domain/marco-normativo.md) |
| *"monolítica limpia … MVC … Arquitectura Hexagonal o Clean"* | [`mvc-hexagonal`](specs/architecture/mvc-hexagonal.md) · [ADR-0001](specs/adr/0001-monolito-mvc-con-vision-hexagonal.md) |
| *"Windows … Android … instalador MSI … APK"* | [`06-distribucion`](docs/arquitectura/06-distribucion-msi-apk.md) · [ADR-0003](specs/adr/0003-estrategia-multiplataforma.md) |
| *"detalle los casos posibles … Nubefact"* | [`casos de uso`](specs/features/casos-de-uso.md) · [`benchmark`](docs/benchmark-facturacion.md) |
| *"estudiando el archivo UBL-Invoice-2.1.xsd"* | [`perfil UBL`](specs/contracts/ubl/perfil-invoice.md) · [`xsd/`](specs/contracts/ubl/xsd/) |

</details>

---

## Alcance

| ✅ Incluye | ❌ No incluye |
|---|---|
| Contratos, DTOs y catálogos | Implementación de los endpoints |
| 24 reglas de negocio numeradas | Cálculo ejecutable de IGV/ISC/ICBPER |
| Diagramas MVC y hexagonal | Código de controladores y adaptadores |
| Puertos (interfaces) en `src/` | Implementación de esos puertos |
| Mock y mapa de pruebas | Tests ejecutados contra la aplicación |
| Matriz normativa y tabla de match | Integración real con OSE/SUNAT |
| **Nada de interfaz de usuario** | Pantallas, wireframes o prototipos |

> El alcance es **especificación técnica**. El contrato API es un contrato de servicio, no una
> pantalla; la restricción MSI/APK se documenta como restricción arquitectónica.

---

## Decisiones que se pueden defender

1. **El contrato manda.** El OpenAPI y los 7 JSON Schemas se escribieron antes que cualquier
   implementación, y el validador comprueba que siguen siendo coherentes.
2. **Un mock, una fuente.** Los datos de prueba viven solo en `tests/mocks/`; no hay copias en `src/`.
3. **Antifraude en los datos.** El DTO de entrada no acepta `totales`, `id`, `estado` ni
   `serie_numero`: el dominio los calcula y los asigna.
4. **El dominio no conoce el framework.** Se verifica con `grep` sobre `src/dominio`; los 5 puertos de
   salida son la frontera.
5. **La validación formal va antes de guardar.** Si el XSD rechaza el XML, no se registra nada.

---

## Documentación

| Documento | Para qué |
|---|---|
| [`00-caso.md`](00-caso.md) | Caso transcrito y requisitos REQ-01..REQ-12 |
| [`01-RESUMEN-EJECUTIVO.md`](01-RESUMEN-EJECUTIVO.md) | Portada y mapa de la entrega |
| [`VERIFICACION.md`](VERIFICACION.md) | Enunciado → evidencia, pruebas y límites |
| [`MEMORIA-TECNICA.docx`](MEMORIA-TECNICA.docx) | Versión consolidada para imprimir |
| [`docs/arquitectura/`](docs/arquitectura/README.md) | Figuras, matriz y documentos de diseño |
| [`specs/`](specs/README.md) | Fuente de verdad: dominio, contratos y ADR |

---

<div align="center">

**Trabajo académico** — Universidad Nacional Agraria de la Selva · Arquitectura de Software · 2026

*Estado: entrega completa de la fase 1. Los límites conocidos están declarados en
[`VERIFICACION.md §4`](VERIFICACION.md).*

</div>
