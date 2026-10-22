# Specifications Directory (`specs/`)

Fuente de verdad del sistema de facturación electrónica: **el contrato manda sobre el código**.
Ninguna línea de lógica de negocio se escribe sin que exista antes aquí.

## Estructura

```text
specs/
├── adr/             decisiones de arquitectura (inmutables)
├── architecture/    requisitos de arquitectura (MVC → Hexagonal)
├── contracts/       contratos formales: OpenAPI, JSON Schemas, catálogos, perfil UBL
├── domain/          modelo de dominio, reglas de negocio y marco normativo
├── features/        casos de uso y criterios de aceptación (Gherkin)
├── templates/       plantillas reutilizables
└── README.md        esta guía
```

## Principios (aplicados a este caso)

1. **Contrato antes que código.** El OpenAPI y los JSON Schemas se aprueban antes de implementar.
2. **Criterios ejecutables.** Cada regla RN-xx de `domain/reglas-negocio.md` tiene un caso de prueba
   asociado en la matriz de trazabilidad.
3. **Documentación viva.** Si la implementación revela que el contrato estaba incompleto, se cambia
   **primero** el contrato.
4. **Interfaces primero.** Los puertos de `src/puertos.py` se derivan de estos contratos, no al revés.

## Qué hay en cada carpeta

| Carpeta | Archivo | Contenido |
|---|---|---|
| `architecture/` | `mvc-hexagonal.md` | 11 requisitos ASR de MVC a Hexagonal |
| `domain/` | `modelo-dominio.md` | 6 entidades, invariantes, máquina de estados, DTOs |
| `domain/` | `reglas-negocio.md` | 24 reglas RN-01..RN-24 (impuestos, numeración, migración) |
| `domain/` | `marco-normativo.md` | normas citadas y su trazabilidad a las reglas |
| `contracts/` | `facturacion-api.yaml` | contrato OpenAPI de 9 rutas + seguridad |
| `contracts/dto/` | `*.schema.json` | 7 JSON Schemas (petición y respuesta) + ejemplos |
| `contracts/catalogs/` | `catalogos-sunat.md` | catálogos 01, 02, 03, 05, 07, **08**, 09, 10, 51 |
| `contracts/ubl/` | `perfil-invoice.md` | perfil UBL 2.1 Invoice (rutas y orden) |
| `features/` | `casos-de-uso.md` | 10 casos de uso + 10 escenarios Gherkin |
| `adr/` | `0001`, `0002`, `0003` | MVC→Hexagonal, UBL/XSD y multiplataforma |

## Cómo proponer un cambio

1. Modifica el contrato o la regla en `specs/`.
2. Actualiza la matriz de trazabilidad (`docs/arquitectura/04-...`).
3. Recién entonces cambia `src/` y `tests/`.

Verificación rápida de que los contratos siguen coherentes:

```bash
python validacion/validar_contratos.py
```
