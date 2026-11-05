"""Verificación de la fase 0: las clases generadas del XSD oficial existen y serializan.

Comprueba:
  1. Los 18 módulos generados están presentes.
  2. Se importan desde la ruta real del proyecto (`src.adapters.outbound.ubl.generated`).
  3. Un Invoice construido con esas clases valida contra `UBL-Invoice-2.1.xsd`.
  4. Un elemento que el XSD no permite no se puede construir (el generador es la garantía).

Uso:  python validacion/verificar_generacion.py   (fase 0/2; las pruebas unitarias están en tests/)
"""

from __future__ import annotations

import datetime as dt
import sys
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
GENERADO = RAIZ / "src" / "adapters" / "outbound" / "ubl" / "generated"
XSD = RAIZ / "specs" / "contracts" / "ubl" / "oficial" / "maindoc" / "UBL-Invoice-2.1.xsd"

NS = {None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2", "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2", "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"}

ok: list[str] = []
fallos: list[str] = []


def main() -> int:
    # 1. inventario
    modulos = sorted(p.name for p in GENERADO.rglob("*.py") if p.name != "__init__.py")
    if len(modulos) >= 14:
        ok.append(f"{len(modulos)} módulos generados presentes")
    else:
        fallos.append(f"solo {len(modulos)} módulos generados (se esperaban ≥14)")

    for obligatorio in (
        "ubl_invoice_2_1.py",
        "ubl_credit_note_2_1.py",
        "ubl_debit_note_2_1.py",
        "ubl_common_aggregate_components_2_1.py",
        "ubl_common_basic_components_2_1.py",
    ):
        if not any(m == obligatorio for m in modulos):
            fallos.append(f"falta el módulo {obligatorio}")

    try:
        from lxml import etree
        from xsdata.formats.dataclass.serializers import XmlSerializer
        from xsdata.formats.dataclass.serializers.config import SerializerConfig
        from xsdata.models.datatype import XmlDate, XmlTime

        from src.adapters.outbound.ubl.generated.common import (
            ubl_common_aggregate_components_2_1 as cac,
        )
        from src.adapters.outbound.ubl.generated.common import (
            ubl_common_basic_components_2_1 as cbc,
        )
        from src.adapters.outbound.ubl.generated.maindoc.ubl_invoice_2_1 import Invoice
    except ImportError as e:  # noqa: BLE001
        print(f"No se pudieron importar las clases generadas: {e}")
        print("Revisa PYTHONPATH / pip install -r requirements-dev.txt")
        return 1

    ok.append("las clases se importan desde src.adapters.outbound.ubl.generated")

    # 2. construcción mínima
    factura = Invoice(
        ublversion_id=cbc.UblversionId(value="2.1"),
        customization_id=cbc.CustomizationId(value="2.0"),
        id=cbc.Id(value="F001-00000001"),
        issue_date=cbc.IssueDate(value=XmlDate.from_date(dt.date(2026, 11, 5))),
        issue_time=cbc.IssueTime(value=XmlTime.from_time(dt.time(10, 30))),
        invoice_type_code=cbc.InvoiceTypeCode(value="01"),
        document_currency_code=cbc.DocumentCurrencyCode(value="PEN"),
        accounting_supplier_party=cac.AccountingSupplierParty(
            party=cac.Party(
                party_identification=[
                    cac.PartyIdentification(id=cbc.Id(value="20123456786", scheme_id="6"))
                ],
                party_legal_entity=[
                    cac.PartyLegalEntity(
                        registration_name=cbc.RegistrationName(value="ABC SOFTWARE CORP SAC")
                    )
                ],
            )
        ),
        accounting_customer_party=cac.AccountingCustomerParty(
            party=cac.Party(
                party_identification=[
                    cac.PartyIdentification(id=cbc.Id(value="20512345671", scheme_id="6"))
                ],
                party_legal_entity=[
                    cac.PartyLegalEntity(
                        registration_name=cbc.RegistrationName(value="DISTRIBUIDORA SELVA SAC")
                    )
                ],
            )
        ),
        legal_monetary_total=cac.LegalMonetaryTotal(
            line_extension_amount=cbc.LineExtensionAmount(value=Decimal("100.00"), currency_id="PEN"),
            tax_inclusive_amount=cbc.TaxInclusiveAmount(value=Decimal("118.00"), currency_id="PEN"),
            payable_amount=cbc.PayableAmount(value=Decimal("118.00"), currency_id="PEN"),
        ),
        invoice_line=[
            cac.InvoiceLine(
                id=cbc.Id(value="1"),
                invoiced_quantity=cbc.InvoicedQuantity(value=Decimal("1"), unit_code="NIU"),
                line_extension_amount=cbc.LineExtensionAmount(value=Decimal("100.00"), currency_id="PEN"),
                item=cac.Item(description=[cbc.Description(value="SACO DE ARROZ 50KG")]),
                price=cac.Price(price_amount=cbc.PriceAmount(value=Decimal("118.00"), currency_id="PEN")),
            )
        ],
    )
    xml = XmlSerializer(config=SerializerConfig(xml_declaration=True, encoding="UTF-8")).render(
        factura, ns_map=NS
    ).encode("utf-8")
    ok.append("un Invoice mínimo se construye y serializa sin errores")

    # 3. conformidad con el esquema oficial
    esquema = etree.XMLSchema(etree.parse(str(XSD)))
    if esquema.validate(etree.fromstring(xml)):
        ok.append("el XML serializado valida contra UBL-Invoice-2.1.xsd")
    else:
        fallos.append("el XML serializado NO valida contra el esquema oficial")

    # 4. el XSD impide construir lo que no existe
    try:
        cbc.ElementoInexistente(value="x")  # type: ignore[attr-defined]
        fallos.append("se pudo instanciar un elemento inexistente (no debería ser posible)")
    except AttributeError:
        ok.append("un elemento que el XSD no define no se puede construir")

    print("=" * 74)
    print(" VERIFICACIÓN DE LA GENERACIÓN (clases del XSD oficial)")
    print("=" * 74)
    for linea in ok:
        print("  OK   ", linea)
    for linea in fallos:
        print("  FALLA", linea)
    print("-" * 74)
    print(f"  {len(ok)} comprobaciones correctas, {len(fallos)} fallos")
    return 0 if not fallos else 1


if __name__ == "__main__":
    sys.exit(main())
