# ADR-0004: Cómo se implementa el puerto `IXmlBuilder`

- **Estado:** Aceptada
- **Fecha:** 2026-11-05
- **Decisores:** Alvarado Ichpas Benny Joshua (arquitectura), área tributaria
- **Relacionada con:** [ADR-0002](0002-ubl-sunat-y-validacion-xsd.md) (esquemas oficiales)

## Contexto

`src/puertos.py` declara `IXmlBuilder`: el dominio necesita convertir un `Comprobante` en XML
UBL 2.1 sin conocer la librería que lo serializa. El Taller 2 exige implementar esa generación
**desde el XSD oficial**, y el primer entregable ya marcó el problema: un "perfil propio" escrito a
mano no demuestra conformidad.

El puerto se definió en la fase 1 con `comprobante: dict`, que no expresa el lenguaje del dominio.
Esta decisión lo corrige: el puerto recibe el **agregado** y el adaptador solo traduce.

## Alternativas consideradas

| Opción | Qué implica | Veredicto |
|---|---|---|
| **A. Plantillas de texto / f-strings** | el XML se arma concatenando; el orden y el escape dependen del programador | **Descartada**: es el defecto que la rúbrica penalizó |
| **B. Construir con `lxml` elemento a elemento** | control total, pero hay que replicar a mano el orden de cientos de elementos | Descartada: el error humano de orden es inevitable |
| **C. Clases generadas desde el XSD (`xsdata`) + serializador** | las clases salen del esquema; el orden y los tipos los impone el estándar; un elemento inexistente no se puede construir | **Elegida** |
| D. Librería UBL de terceros | dependencia opaca, difícil de auditar | Descartada |

## Decisión

1. **Las clases se generan desde el XSD oficial**, no se escriben a mano:
   `scripts/generar_clases_ubl.ps1` ejecuta `xsdata generate` sobre
   `specs/contracts/ubl/oficial/maindoc` y produce `src/adaptadores/salida/ubl/generated/`.
   Esas clases se **versionan**; si cambian sin tocar el XSD, algo raro pasó.
2. El adaptador `GeneradorUblXsdata` implementa el puerto `IXmlBuilder` (`construir`) y traduce
   el agregado del dominio a esas clases: cabecera, partes, líneas, tributos, totales y forma de
   pago. **No calcula nada**: los importes vienen ya calculados por el dominio.
3. El XML se genera **sin firma**; el adaptador de firma agrega `ext:UBLExtensions` después.
4. El orden del flujo es el de la RN-18: **generar → validar contra el esquema oficial → firmar
   → enviar**. La validación es el puerto `IValidadorXsd` (ADR-0002).

## Consecuencias

**Positivas**

- El XML no puede tener un elemento fuera del esquema ni en orden incorrecto: lo impide la clase.
- El serializador escapa `&`, `<` y `>` por construcción.
- La conformidad se demuestra ejecutando las pruebas (147) y validando contra OASIS.

**Negativas**

- El repositorio guarda ~3 MB de clases generadas.
- Regenerar exige `xsdata[cli]` y `ruff` (que `xsdata` usa para formatear la salida).

## Verificación

| Verificación | Criterio |
|---|---|
| El puerto está tipado | `IXmlBuilder.construir(comprobante: Comprobante) -> bytes` |
| El adaptador lo implementa | `isinstance(GeneradorUblXsdata(), IXmlBuilder)` |
| Salida conforme | los 6 escenarios validan contra los XSD oficiales (`test_rn18_conformidad_esquema.py`) |
| Nada se escribe a mano | las clases de `generated/` se regeneran con el script y no se editan |
