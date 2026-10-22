# Perfil UBL 2.1 — Invoice (factura y boleta)

**Base normativa:** estándar **UBL 2.1** (OASIS), esquema `UBL-Invoice-2.1.xsd`, con el perfil de
comprobantes electrónicos exigido por SUNAT.

Este documento **no copia** el XSD completo (miles de campos): define el **perfil** — el subconjunto
ordenado de elementos que el sistema emite — y su correspondencia con los datos del dominio.

> El análisis del esquema oficial (`UBL-Invoice-2.1.xsd`) está en la **sección 7**.

---

## 1. Namespaces

| Prefijo | URI | Uso |
|---|---|---|
| (default) | `urn:oasis:names:specification:ubl:schema:xsd:Invoice-2` | raíz `Invoice` |
| `cac` | `urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2` | agregados (Party, InvoiceLine…) |
| `cbc` | `urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2` | componentes simples (ID, Amount…) |
| `ext` | `urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2` | extensiones (firma) |
| `ds` | `http://www.w3.org/2000/09/xmldsig#` | firma digital |
| `xsi` | `http://www.w3.org/2001/XMLSchema-instance` | validación |

## 2. Estructura del documento (orden obligatorio)

```text
Invoice
├── ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature   (firma)
├── cbc:UBLVersionID                          "2.1"
├── cbc:CustomizationID                       perfil SUNAT
├── cbc:ID                                    F001-00000123
├── cbc:IssueDate                             2026-10-22
├── cbc:IssueTime                             09:15:00
├── cbc:InvoiceTypeCode                       "01" (listID = tipo operación)
├── cbc:Note                                  leyendas (monto en letras, observaciones)
├── cbc:DocumentCurrencyCode                  PEN
├── cbc:LineCountNumeric                      3
├── cac:AccountingSupplierParty               emisor
│   └── cac:Party
│       ├── cac:PartyIdentification/cbc:ID    RUC (@schemeID=6)
│       ├── cac:PartyName/cbc:Name            nombre comercial
│       └── cac:PartyLegalEntity
│           ├── cbc:RegistrationName
│           └── cac:RegistrationAddress       ubigeo + dirección
├── cac:AccountingCustomerParty               receptor
│   └── cac:Party
│       ├── cac:PartyIdentification/cbc:ID    doc (@schemeID = catálogo 8)
│       └── cac:PartyLegalEntity
├── cac:PaymentTerms                          forma de pago / cuotas
├── cac:TaxTotal                              totales de impuestos
│   └── cac:TaxSubtotal
│       ├── cbc:TaxableAmount
│       ├── cbc:TaxAmount
│       └── cac:TaxCategory
│           ├── cbc:Percent
│           └── cac:TaxScheme/cbc:ID          catálogo 5
├── cac:LegalMonetaryTotal
│   ├── cbc:LineExtensionAmount
│   ├── cbc:TaxInclusiveAmount
│   └── cbc:PayableAmount
└── cac:InvoiceLine                          1..n
    ├── cbc:ID
    ├── cbc:InvoicedQuantity (@unitCode)     catálogo 3
    ├── cbc:LineExtensionAmount
    ├── cac:AllowanceCharge                  descuento (opcional)
    ├── cac:TaxTotal/cac:TaxSubtotal         tributos de la línea
    ├── cac:Price/cbc:PriceAmount            valor unitario sin IGV
    ├── cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount  precio con IGV
    └── cac:Item
        ├── cbc:Description
        └── cac:SellersItemIdentification/cbc:ID
```

> **El orden importa.** El XSD valida secuencia: si un `cac:TaxTotal` va antes de
> `cac:InvoiceLine`, el documento es inválido aunque los datos sean correctos.

## 3. Ejemplo de XML del perfil

El ejemplo completo y **validado contra el XSD** está en
[`ejemplo-invoice.xml`](ejemplo-invoice.xml): factura `F001-00000123`, tres líneas
(gravada al 18%, exonerada y bolsa plástica con ICBPER), total **S/ 530.00**.

Extracto mínimo:

```xml
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
  <cbc:ID>F001-00000123</cbc:ID>
  <cbc:InvoiceTypeCode listID="0101">01</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>PEN</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty>...</cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty>...</cac:AccountingCustomerParty>
  <cac:LegalMonetaryTotal>
    <cbc:LineExtensionAmount currencyID="PEN">449.83</cbc:LineExtensionAmount>
    <cbc:TaxInclusiveAmount currencyID="PEN">520.00</cbc:TaxInclusiveAmount>
    <cbc:PayableAmount currencyID="PEN">530.00</cbc:PayableAmount>
  </cac:LegalMonetaryTotal>
  <cac:InvoiceLine>...</cac:InvoiceLine>
</Invoice>
```


## 4. Diferencias entre Invoice y CreditNote

| Concepto | `Invoice` (01, 03) | `CreditNote` (07) |
|---|---|---|
| Elemento raíz | `Invoice` | `CreditNote` |
| Tipo de documento | `cbc:InvoiceTypeCode` | `cbc:CreditNoteTypeCode` |
| Motivo | — | `cbc:DiscrepancyResponse/cbc:ResponseCode` (catálogo 9) |
| Referencia | — | `cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID` |
| Líneas | `cac:InvoiceLine` | `cac:CreditNoteLine` |

## 5. Cómo se valida

1. El XML se genera con los namespaces y el **orden** de la sección 2.
2. Se firma con XMLDSig (el certificado vive en el servidor).
3. Se valida contra el XSD del perfil (`UBL-Invoice-2.1.xsd` + extensiones de firma).
4. Solo si valida, se envía a la OSE/SUNAT.

**Regla de oro:** un XML que no valida contra el XSD **no se envía** y el comprobante no se marca
como emitido.

## 6. Qué falta de este perfil (declarado)

| Elemento | Estado | Motivo |
|---|---|---|
| `cac:AdditionalDocumentReference` (detracción, orden de compra) | pendiente | no forma parte del alcance del examen |
| `cac:Delivery` (datos de entrega) | pendiente | se agrega cuando el negocio lo exija |
| `cac:PrepaidPayment` (anticipos) | pendiente | operación no incluida |
| Resumen diario y comunicación de baja | pendiente | fase posterior (REQ-07 parcial) |

---

## 7. El XSD oficial (`UBL-Invoice-2.1.xsd`) y cómo se deriva el perfil

### 7.1 De dónde sale

| Dato | Valor |
|---|---|
| Organización | **OASIS** — Universal Business Language 2.1 |
| Especificación | <https://docs.oasis-open.org/ubl/os-UBL-2.1/> |
| Documento principal | `UBL-Invoice-2.1.xsd` (carpeta `xsd/maindoc/`) |
| Dependencias | `UBL-CommonBasicComponents-2.1.xsd`, `UBL-CommonAggregateComponents-2.1.xsd`, `UBL-CommonExtensionComponents-2.1.xsd`, `UBL-QualifiedDatatypes-2.1.xsd` |
| Extensión peruana | SUNAT agrega el bloque de firma y las reglas de catálogos sobre el estándar |

### 7.2 Extracto del esquema (simplificado para lectura)

```xml
<!-- UBL-Invoice-2.1.xsd — extracto didáctico, se omiten elementos -->
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
            xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
            targetNamespace="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
            elementFormDefault="qualified">

  <xsd:import namespace=".../CommonAggregateComponents-2" schemaLocation="..."/>
  <xsd:import namespace=".../CommonBasicComponents-2"     schemaLocation="..."/>

  <!-- El documento raíz -->
  <xsd:element name="Invoice" type="InvoiceType"/>

  <xsd:complexType name="InvoiceType">
    <xsd:complexContent>
      <!-- hereda de DocumentType: UBLVersionID, CustomizationID, ID,
           IssueDate, IssueTime, Note, DocumentCurrencyCode, LineCountNumeric... -->
      <xsd:extension base="cac:DocumentType">
        <xsd:sequence>
          <xsd:element ref="cac:AccountingSupplierParty"/>
          <xsd:element ref="cac:AccountingCustomerParty"/>
          <xsd:element ref="cac:PaymentMeans" minOccurs="0" maxOccurs="unbounded"/>
          <xsd:element ref="cac:TaxTotal" minOccurs="0" maxOccurs="unbounded"/>
          <xsd:element ref="cac:LegalMonetaryTotal"/>
          <xsd:element ref="cac:InvoiceLine" maxOccurs="unbounded"/>
        </xsd:sequence>
      </xsd:extension>
    </xsd:complexContent>
  </xsd:complexType>

  <!-- Un dato básico del estándar: los montos llevan moneda como atributo -->
  <xsd:element name="PayableAmount" type="cbc:AmountType"/>
  <xsd:complexType name="AmountType">
    <xsd:simpleContent>
      <xsd:extension base="xsd:decimal">
        <xsd:attribute name="currencyID" type="xsd:string" use="required"/>
      </xsd:extension>
    </xsd:simpleContent>
  </xsd:complexType>
</xsd:schema>
```

**Tres lecciones que salen del archivo:**

1. **El orden es contrato.** `InvoiceType` es una **secuencia**: un `cac:TaxTotal` después de
   `cac:InvoiceLine` invalida el documento aunque los datos sean correctos.
2. **La moneda va en los importes.** En el esquema de OASIS los atributos `currencyID`/`unitCode`
   son opcionales, pero **SUNAT los exige**: el perfil los vuelve obligatorios. Olvidarlos es el
   error más común al generar el XML a mano.
3. **El estándar es permisivo; SUNAT no.** El XSD acepta `minOccurs="0"` en muchos campos, pero el
   perfil peruano los vuelve obligatorios (por ejemplo, el documento del receptor y su ubigeo).

### 7.3 Cómo se deriva nuestro perfil

```text
  XSD oficial (OASIS)          Perfil SUNAT              Nuestro perfil           DTO / dominio
  ─────────────────────  →  ───────────────────  →  ─────────────────────  →  ──────────────────
  InvoiceType (60+ elem.)     campos obligatorios      los campos de la matriz (59 cruces)      7 JSON Schemas
```

| Decisión del perfil | Justificación |
|---|---|
| se conservan los namespaces oficiales | el XML debe ser interoperable |
| se respeta la secuencia del estándar | el XSD es posicional |
| se recortan elementos no usados (Delivery, PrepaidPayment) | el sistema no los opera todavía |
| se vuelven obligatorios los campos que SUNAT exige | el XSD no basta para aprobar ante SUNAT |

### 7.4 Correspondencia directa XSD ↔ dominio

| Elemento del XSD | Tipo del estándar | En nuestro perfil | Campo del dominio |
|---|---|---|---|
| `cbc:UBLVersionID` | `xsd:string` | obligatorio, valor `2.1` | constante |
| `cbc:InvoiceTypeCode` | `xsd:string` + `listID` | catálogo 01 + catálogo 51 en `listID` | `Comprobante.tipo`, `tipoOperacion` |
| `cbc:DocumentCurrencyCode` | `xsd:string` | catálogo 02 | `Comprobante.moneda` |
| `cbc:ID` | `xsd:string` | serie + correlativo | `Comprobante.numero` |
| `cac:AccountingSupplierParty` | agregado | obligatorio | `Empresa` |
| `cac:AccountingCustomerParty` | agregado | obligatorio | `Cliente` |
| `cac:TaxTotal/cbc:TaxAmount` | `AmountType` (currencyID) | obligatorio | `Totales.totalIgv` |
| `cac:InvoiceLine/cbc:InvoicedQuantity` | `QuantityType` (unitCode) | obligatorio | `LineaDetalle.cantidad` |
| `cac:LegalMonetaryTotal/cbc:PayableAmount` | `AmountType` (currencyID) | obligatorio | `Totales.importeTotal` |

### 7.5 Estado de la validación

**Materializado y verificado.** El perfil está escrito como XSD en
[`xsd/`](xsd/) (`Invoice-2-profile.xsd` + los dos componentes) y el XML de ejemplo
([`ejemplo-invoice.xml`](ejemplo-invoice.xml)) se valida contra él:

```bash
python validacion/validar_xml_ubl.py
```

Resultado: **6 comprobaciones, 0 fallos** — el XML valida, un XML sin `cbc:ID` es rechazado y la
aritmética de totales cuadra.

| Archivo | Contenido |
|---|---|
| `xsd/Invoice-2-profile.xsd` | raíz `Invoice`, orden obligatorio de elementos |
| `xsd/CommonBasicComponents-2.xsd` | componentes simples (`cbc:`) con sus atributos |
| `xsd/CommonAggregateComponents-2.xsd` | agregados (`cac:`) y elementos globales |
| `ejemplo-invoice.xml` | el mismo comprobante que el DTO JSON, en UBL |

> **Hallazgo del ejercicio:** una cantidad negativa **pasa** el XSD (porque `xs:decimal` lo admite)
> pero la rechaza la regla RN-14. Eso demuestra por qué el diseño tiene **dos capas de validación**:
> el esquema no reemplaza a las reglas de negocio.
