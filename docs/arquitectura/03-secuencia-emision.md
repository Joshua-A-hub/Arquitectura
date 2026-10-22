# Flujo de emisión — secuencia

Complementa los diagramas de arquitectura. Muestra **quién llama a quién** y **dónde se corta** el
proceso cuando algo no cumple.

```mermaid
sequenceDiagram
    autonumber
    participant U as Operador
    participant C as Controlador (REST)
    participant D as Dominio (Reglas)
    participant R as Repositorio
    participant X as Generador XML
    participant S as Firma + XSD
    participant O as OSE / SUNAT

    U->>C: POST /comprobantes
    C->>C: validar DTO (JSON Schema)
    alt DTO inválido
        C-->>U: 400 VALIDACION_ESQUEMA
    end
    C->>D: emitir(comando)
    D->>D: RN-01..RN-17 (RUC, catálogo 8, fechas, detalle)
    alt regla incumplida
        D-->>U: 400 VALIDACION_NEGOCIO
    end
    D->>R: siguiente correlativo
    R-->>D: F001-00000123
    D->>D: calcular IGV / ISC / ICBPER y totales
    D->>X: construir Invoice UBL
    X-->>S: XML sin firmar
    S->>S: firmar (XMLDSig)
    S->>S: validar contra XSD
    alt XSD inválido
        S-->>U: 500 XML_INVALIDO (no se registra)
    end
    S->>O: enviar comprobante
    O-->>S: CDR (código 0)
    S->>R: guardar comprobante + XML + CDR
    R-->>C: registro
    C-->>U: 201 {serie_numero, estado ACEPTADO, hash, xml_url}
```

## Lectura en palabras

1. **Nada se guarda** hasta que el XML valida. El orden es la garantía: primero se comprueba, después
   se persiste.
2. El **correlativo** se asigna dentro de la transacción: si la emisión falla, no se consume.
3. La **firma** ocurre antes de la validación XSD, y el perfil **admite** el bloque de extensión
   (`ext:UBLExtensions`) donde viaja la firma; validar la firma en sí es trabajo de fase 2.
4. El **CDR** se almacena junto al XML: es la evidencia de que SUNAT aceptó el documento.
5. Un fallo de red **no reemite**: deja el comprobante en `PENDIENTE_ENVIO` (RN-20).
