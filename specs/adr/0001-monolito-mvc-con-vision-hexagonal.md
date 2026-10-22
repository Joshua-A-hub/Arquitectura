# ADR-0001: Monolito MVC ahora, hexagonal después

- **Estado:** Aceptada
- **Fecha:** 2026-10-22
- **Decisores:** Líder de arquitectura, equipo de desarrollo

## Contexto

ABC Software Corp necesita salir de un software básico de almacén sin arquitectura. La gerencia exige
una primera versión **monolítica limpia con MVC**, pero también que el diseño permita migrar a
**hexagonal/Clean** y luego a microservicios cuando el volumen crezca.

## Opciones consideradas

1. **Monolito MVC sin más** — rápido, pero deja el dominio acoplado a la UI y a la base de datos.
2. **Hexagonal desde el día uno** — ideal, pero duplica esfuerzo en la primera entrega.
3. **Monolito MVC con las fronteras ya dibujadas** — MVC como estructura visible, con el dominio
   aislado tras interfaces.

## Decisión

Se elige la **opción 3**. El código se organiza en capas MVC, pero **las dependencias hacia afuera
se declaran como interfaces** (`IComprobanteRepository`, `ISunatGateway`, `IXmlBuilder`) que hoy
tienen una implementación concreta (SQLite, cliente OSE). Las reglas de negocio viven en servicios de
dominio que **no importan el framework web**.

## Consecuencias

**Positivas**
- Se entrega rápido, con MVC reconocible para el equipo.
- La migración a hexagonal es cambiar implementaciones, no reescribir reglas.
- Las reglas RN-01..RN-24 se prueban sin levantar servidor ni base de datos.

**Negativas**
- Hay un costo inicial de interfaces que en un MVC "puro" no existirían.
- Exige disciplina: cualquiera puede romper la regla de dependencia importando el framework en el
  dominio. Se controla con revisión y con la prueba `grep -r "import fastapi" src/dominio`.

## Cómo se verifica

| Verificación | Criterio |
|---|---|
| Dominio aislado | `grep -r "fastapi\|sqlite" src/dominio` no devuelve nada |
| Puertos definidos | existen los 5 puertos de salida en `src/puertos.py` |
| Migración posible | la tabla de equivalencia MVC↔Hexagonal está en `docs/arquitectura/README.md` |
