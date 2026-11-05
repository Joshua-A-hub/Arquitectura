# ADR-0002: Esquemas oficiales de UBL 2.1, clases generadas y validación antes de firmar

- **Estado:** Aceptada (sustituye la decisión anterior de "perfil propio")
- **Fecha:** 2026-10-22 · **Revisada:** 2026-11-04
- **Decisores:** Líder de arquitectura, área tributaria

## Contexto

SUNAT exige comprobantes estructurados bajo **UBL 2.1**. El sistema anterior no genera XML, no firma y
no se comunica con una OSE. Un XML inválido genera rechazo y observaciones tributarias.

La versión anterior de este ADR decidió validar contra un **perfil propio** (tres XSD escritos a mano,
de 2–6 KB) en lugar del esquema oficial. Eso **no demuestra conformidad con UBL 2.1**: valida contra
una copia del error. El esquema oficial de `Invoice` son ~60 KB más ~2.6 MB de componentes comunes.

## Opciones consideradas

| Opción | Qué implica | Veredicto |
|---|---|---|
| 1. Plantillas de texto | XML armado a mano; sin garantía de estructura | **Descartada** |
| 2. Librería UBL de terceros | dependencia opaca, difícil de auditar | Descartada |
| 3. Perfil propio (decisión anterior) | XSD hecho a medida; valida contra sí mismo | **Descartada** |
| **4. Esquemas oficiales + clases generadas** | XSD de OASIS en el repo; clases generadas con `xsdata`; validación antes de firmar | **Elegida** |

## Decisión

1. **Los esquemas oficiales viven en el repositorio**: `specs/contracts/ubl/oficial/maindoc/`
   (`UBL-Invoice-2.1.xsd`, `UBL-CreditNote-2.1.xsd`, `UBL-DebitNote-2.1.xsd`) y
   `specs/contracts/ubl/oficial/common/` (todos sus imports, incluidos XMLDSig y XAdES).
2. **El XML no se escribe a mano**: se generan clases desde el XSD oficial con **`xsdata`** (el
   proyecto ya usa Python) y se serializa con ellas. Comando de referencia:

   ```bash
   xsdata generate specs/contracts/ubl/oficial/maindoc/UBL-Invoice-2.1.xsd \
       --package src.ubl.invoice
   ```

   El perfil SUNAT (`specs/contracts/ubl/perfil-invoice.md`) sigue existiendo, pero como **restricción
   de negocio adicional** (qué campos son obligatorios para SUNAT), **nunca** como sustituto del
   esquema oficial.
3. **Se valida antes de firmar** y se vuelve a verificar la estructura después de firmar.

## Orden obligatorio del flujo

```text
validar DTO → validar reglas de negocio → calcular (IGV, ISC por sistema, ICBPER) →
generar XML → VALIDAR contra el esquema oficial → firmar (XMLDSig) →
verificar que la firma no alteró la estructura → enviar a OSE → guardar CDR
```

**Por qué antes de firmar:** si la validación obliga a corregir el documento, la firma previa queda
invalidada y habría que firmar de nuevo. Firmar un XML que no cumple el esquema es trabajo perdido.

## Consecuencias

**Positivas**
- La conformidad con UBL 2.1 se demuestra contra el estándar, no contra una copia.
- Las clases generadas eliminan el error humano de orden y de nombres de elemento.
- El error se detecta en casa, antes de firmar y antes de SUNAT.

**Negativas**
- El repositorio crece ~2.7 MB (esquemas oficiales) y se regenera si OASIS publica versión nueva.
- `xsdata` añade una dependencia de generación (no de ejecución).
- El perfil SUNAT hay que mantenerlo como documento de reglas, no como esquema.

## Decisión complementaria: el certificado no vive en el cliente

La firma se realiza **en el servicio**. El certificado es un secreto de la empresa: si viaja al
dispositivo, se puede extraer.

## Verificación

| Verificación | Criterio |
|---|---|
| Esquema oficial presente | `maindoc/UBL-Invoice-2.1.xsd` + `common/` compilan con lxml |
| Conformidad | el XML de ejemplo valida contra el esquema oficial (ver `informe-xsd-oficial.md`) |
| Orden del flujo | la secuencia y RN-18 colocan la validación **antes** de la firma |
| Generación | el comando de `xsdata` está documentado y las clases son reproducibles |
| Firma | el XML contiene `ds:Signature` y el hash se guarda |
