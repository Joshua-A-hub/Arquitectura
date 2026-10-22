# ADR-0002: UBL 2.1 como contrato, validación contra XSD antes de enviar

- **Estado:** Aceptada
- **Fecha:** 2026-10-22
- **Decisores:** Líder de arquitectura, área tributaria

## Contexto

SUNAT exige comprobantes estructurados bajo **UBL 2.1** (`UBL-Invoice-2.1.xsd`). El sistema anterior
no genera XML, no firma y no se comunica con una OSE. Un XML inválido enviado a SUNAT genera rechazo
y, en el peor caso, observaciones tributarias.

## Opciones consideradas

1. Generar el XML a mano con plantillas de texto.
2. Usar una librería UBL de terceros.
3. Definir un **perfil propio** derivado del XSD de UBL 2.1 y validar formalmente antes de enviar.

## Decisión

Se elige la **opción 3**: el contrato de datos del dominio se documenta como **perfil SUNAT** con las
rutas exactas del XSD (`specs/contracts/ubl/perfil-invoice.md`), y **ningún XML sale del sistema sin
validar contra el XSD**.

Orden obligatorio del flujo de emisión:

```text
validar DTO → validar reglas de negocio → calcular totales →
generar XML → firmar (XMLDSig) → validar contra XSD → enviar a OSE → guardar CDR
```

## Consecuencias

**Positivas**
- El error se detecta en casa, no en SUNAT.
- La matriz de trazabilidad se puede auditar campo por campo.
- El perfil es estable: si SUNAT cambia de versión, cambia un solo artefacto.

**Negativas**
- Mantener el perfil es trabajo continuo.
- La firma digital requiere un certificado y gestión de claves (fuera del alcance de esta fase).

## Decisión complementaria: el certificado no vive en el cliente

La firma se realiza **en el servicio**, nunca en la app de escritorio o móvil. El certificado es un
secreto de la empresa: si viaja al dispositivo, se puede extraer.

## Verificación

| Verificación | Criterio |
|---|---|
| Perfil documentado | cada campo del comprobante tiene ruta UBL en la matriz |
| Validación formal | un XML inválido es rechazado y no se registra |
| Firma | el XML contiene `ds:Signature` y el hash se guarda |
