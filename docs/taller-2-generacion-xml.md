# Taller 2 (2.º parcial): generación del XML a partir de `UBL-Invoice-2.1.xsd`

> **Enunciado.** Implementar la generación de XML a partir del XSD Invoice 2.1, en el lenguaje del
> dominio. La evaluación serán pruebas unitarias de generación. Fecha límite: 05/11/2026.

**Respuesta en una línea.** Las clases Python se **generan desde los XSD oficiales con `xsdata`**; un
adaptador traduce el agregado del dominio (`Comprobante`, `Linea`, `Totales`, `FormaPago`…) a esas
clases y las serializa; **159 pruebas unitarias** verifican cada bloque del XML, su conformidad con el
esquema oficial y la regresión contra XML de referencia.

```powershell
pip install -r requirements-dev.txt
pytest tests/unit -q           # 159 pruebas (115 de generación + 44 de dominio)
```

---

## 1. Del XSD a las clases: nada se escribe a mano

```text
specs/contracts/ubl/oficial/        (16 XSD oficiales de OASIS)
        │  xsdata generate
        ▼
src/adaptadores/salida/ubl/generated/  (dataclasses tipadas: Invoice, InvoiceLine, TaxSubtotal…)
        │  GeneradorUblXsdata
        ▼
dominio (Comprobante · Linea · Totales · FormaPago)
        │
        ▼
XML UBL 2.1 ──► validador lxml contra el XSD oficial (antes de firmar, RN-18)
```

- **Las clases salen del XSD.** El XSD es la fuente: `xsdata` produce una dataclass por tipo de UBL.
  Se regeneran con `scripts/generar_clases_ubl.ps1`.
- **No hay plantillas ni concatenación.** Por eso el serializador escapa `&`, `<` y `>` y el orden lo
  impone el esquema: un elemento que no existe en el XSD **ni siquiera se puede construir**.
- **Validación con el esquema oficial completo**: `specs/contracts/ubl/oficial/` incluye `Invoice`,
  `CreditNote`, `DebitNote` y sus 13 componentes (incluidos XMLDSig y XAdES).

## 2. «En el lenguaje del dominio»

El generador **no recibe JSON ni diccionarios**: recibe el agregado `Comprobante`. El cálculo (IGV,
ISC, ICBPER, totales, cuotas) ya lo hizo el dominio; el generador **solo traduce**.

| Término del dominio (`src/dominio`) | Elemento UBL 2.1 que genera |
|---|---|
| `Comprobante.tipo` (factura/boleta → `Invoice`; NC → `CreditNote`; ND → `DebitNote`) | elemento raíz |
| `Comprobante.serie_numero` | `cbc:ID` (`F001-00000123`) |
| `Comprobante.tipo_operacion` | `cbc:InvoiceTypeCode/@listID` (catálogo 51) |
| `Comprobante.monto_en_letras` | `cbc:Note[@languageLocaleID='1000']` |
| `len(Comprobante.lineas)` | `cbc:LineCountNumeric` |
| `Emisor` | `cac:AccountingSupplierParty` (RUC, ubigeo, establecimiento) |
| `Cliente.documento` | `cac:AccountingCustomerParty` (catálogo 06) |
| `Linea` | `cac:InvoiceLine` / `CreditNoteLine` / `DebitNoteLine` |
| `Linea.unidad` | `cbc:InvoicedQuantity/@unitCode` (catálogo 03) |
| `Linea.afectacion` | `cac:TaxCategory/cbc:TaxExemptionReasonCode` (catálogo 07) |
| `Linea.isc.sistema` | `cac:TaxCategory/cbc:TierRange` (catálogo 08) + TaxScheme `2000` |
| `Linea.aplica_icbper` | `cac:TaxSubtotal[7152]` con `PerUnitAmount` y `BaseUnitMeasure` |
| `Linea.descuento` | `cac:AllowanceCharge` (`ChargeIndicator=false`) |
| `Totales` | `cac:TaxTotal` + `cac:LegalMonetaryTotal` (en ND: `RequestedMonetaryTotal`) |
| `FormaPago` / `Cuota` | `cac:PaymentTerms` (`FormaPago`, `Cuota001`, `PaymentDueDate`) |
| `Comprobante.referencia` / `motivo` | `cac:BillingReference` + `cac:DiscrepancyResponse` |
| `Comprobante.documentos_legado` | `cac:AdditionalDocumentReference` (tipo `99`) |

Código: [`src/adaptadores/salida/ubl/generador.py`](../src/adaptadores/salida/ubl/generador.py). El
generador implementa el puerto `IXmlBuilder` de [`src/puertos.py`](../src/puertos.py).

## 3. Pruebas unitarias de generación

Están en [`tests/unit/generacion_xml/`](../tests/unit/generacion_xml). Todas parten de objetos del
dominio construidos por [`fabrica.py`](../tests/unit/generacion_xml/fabrica.py), sin HTTP ni base
de datos.

| Archivo | Qué verifica | Pruebas |
|---|---|:--:|
| [`test_cabecera.py`](../tests/unit/generacion_xml/test_cabecera.py) | Raíz según el tipo, `UBLVersionID` 2.1, `CustomizationID` 2.0, `cbc:ID` = `serie_numero`, fecha/hora, `InvoiceTypeCode` + catálogo 51, moneda en el documento **y en cada importe**, leyenda 1000 | 17 |
| [`test_partes.py`](../tests/unit/generacion_xml/test_partes.py) | RUC, razón social, ubigeo, dirección y **establecimiento** del emisor; cliente con RUC, DNI, consumidor final y no domiciliado (catálogo 06); escape de `&` | 14 |
| [`test_lineas.py`](../tests/unit/generacion_xml/test_lineas.py) | Una línea por línea del dominio, `unitCode` del catálogo 03, valor y precio unitario, descripción y código, **orden del XSD**, `LineCountNumeric`, **descuento con `AllowanceCharge`** | 19 |
| [`test_tributos.py`](../tests/unit/generacion_xml/test_tributos.py) | IGV 18 %, exonerado (`9997`), inafecto (`9998`), exportación (`9995`), **ISC de los tres sistemas del catálogo 08** (`TierRange`), ICBPER, base del IGV de la línea y global (**reglas SUNAT 3108 y 3277**), cuadre de subtotales y 2 decimales | 15 |
| [`test_totales_pago_referencias.py`](../tests/unit/generacion_xml/test_totales_pago_referencias.py) | Total monetario, `PayableAmount` = total con impuestos, forma de pago contado y crédito con cuotas, discrepancia y referencia de las notas, `RequestedMonetaryTotal` en ND, documento del legado | 12 |
| [`test_conformidad_regresion.py`](../tests/unit/generacion_xml/test_conformidad_regresion.py) | Los 8 escenarios **validan contra el XSD oficial**, determinismo, caracteres especiales, **regresión byte a byte** contra XML de referencia | 21 |
| [`test_dominio.py`](../tests/unit/test_dominio.py) | RUC (módulo 11), serie alfanumérica, valor unitario, IGV, ISC de los tres sistemas, **redondeo sobre la base exacta**, ICBPER, importe en letras, cuotas, reglas RN-02/RN-14 | 44 |

### XML de referencia («golden files»)

[`esperados/`](../tests/unit/generacion_xml/esperados) guarda el XML exacto de cada escenario: si un
cambio altera el XML, la regresión falla y obliga a revisar la diferencia. Para regenerarlos cuando el
cambio es intencional:

```powershell
$env:ACTUALIZAR_ESPERADOS="1"; pytest tests/unit/generacion_xml; Remove-Item Env:ACTUALIZAR_ESPERADOS
```

### Las pruebas encontraron errores reales

| Error | Cómo se detectó | Corrección |
|---|---|---|
| El IGV de la bolsa daba **1.52 en vez de 1.53** | Prueba del comprobante de ejemplo (530.00) | El impuesto se calcula sobre la base exacta y se redondea al final (RN-08) |
| Líneas **exoneradas/inafectas declaraban el tributo `1000`** (IGV) | Prueba de los tributos por afectación | Usan el tributo de su afectación (`9997`, `9998`, `9995`) |
| RN-02 **rechazaba la exportación** (factura exige RUC) | Escenario de exportación en USD | La exportación admite al no domiciliado (catálogo 06 = `0`) |
| Faltaban `LineCountNumeric` y `AllowanceCharge` que **la propia matriz exige** | Auditoría de la suite contra la matriz (filas 9 y 32) | Se añadieron al generador y sus pruebas |
| Las cuotas no se validaban contra el total | Auditoría (RN-16) | `Comprobante` exige que las cuotas sumen el importe total |

## 4. Cómo se ejecuta

```powershell
pip install -r requirements-dev.txt
pytest tests/unit -q

# Generar el XML desde una CLI (segundo adaptador de entrada):
python -m src.cli generar-xml specs/contracts/dto/ejemplo-comprobante.json --salida out
```

## 5. Límites declarados

- **No se firma**: el tallar evalúa generación; el adaptador de firma (`IFirmaDigital`) agrega
  `ext:UBLExtensions` en la fase 2. El orden queda fijado: generar → validar → firmar → enviar.
- **No se envía a SUNAT**: la OSE es un puerto (`ISunatGateway`) sin adaptador todavía.
- Las notas de crédito/débito se generan y validan contra sus XSD oficiales, pero las pruebas se
  centran en `Invoice`, que es el alcance del taller.
