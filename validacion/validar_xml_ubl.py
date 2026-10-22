"""Valida el XML del perfil contra el XSD y reconcilia sus totales.

Comprobaciones:
  1. El XML de ejemplo valida contra el XSD del perfil.
  2. Un XML sin número de comprobante es rechazado (la validación sirve de algo).
  3. LineCountNumeric coincide con la cantidad real de líneas.
  4. El IGV de cabecera coincide con la suma del IGV de las líneas.
  5. La base de cada línea (TaxableAmount) coincide con su LineExtensionAmount.
  6. La suma de líneas coincide con el total del comprobante.
  7. valor + IGV = TaxInclusiveAmount y + ICBPER = PayableAmount.
  8. Un XML con el IGV de cabecera adulterado es detectado (control negativo real).

Depende de lxml (requirements.txt). Si falta, el script no mata el proceso: informa y sale con 1.
"""

from __future__ import annotations

import copy
import sys
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DIR_UBL = RAIZ / "specs" / "contracts" / "ubl"
RUTA_XSD = DIR_UBL / "xsd" / "Invoice-2-profile.xsd"
RUTA_XML = DIR_UBL / "ejemplo-invoice.xml"

NS = {
    "inv": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

ok: list[str] = []
fallos: list[str] = []


def _importar_lxml():
    try:
        from lxml import etree  # noqa: PLC0415

        return etree
    except ImportError:
        return None


def decimal(nodo) -> Decimal:
    return Decimal((nodo.text or "0").strip())


def _ruc_valido(ruc: str) -> bool:
    """Dígito verificador del RUC (RN-01): módulo 11 con factores 5,4,3,2,7,6,5,4,3,2."""
    if not (len(ruc) == 11 and ruc.isdigit()):
        return False
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(d) * f for d, f in zip(ruc[:10], factores))
    resto = suma % 11
    digito = 11 - resto
    if digito == 10:
        digito = 0
    elif digito == 11:
        digito = 1
    return digito == int(ruc[10])


def main() -> int:
    etree = _importar_lxml()
    if etree is None:
        print("Falta lxml. Instálalo con:  pip install -r requirements.txt")
        return 1

    esquema = etree.XMLSchema(etree.parse(str(RUTA_XSD)))

    def validar(xml_bytes: bytes) -> list[str]:
        documento = etree.fromstring(xml_bytes)
        if esquema.validate(documento):
            return []
        return [f"línea {e.line}: {e.message}" for e in esquema.error_log]

    xml = RUTA_XML.read_bytes()
    arbol = etree.fromstring(xml)

    # 1
    errores = validar(xml)
    if errores:
        fallos.append("El XML de ejemplo NO valida: " + " | ".join(errores[:3]))
    else:
        ok.append("ejemplo-invoice.xml valida contra Invoice-2-profile.xsd")

    # 2
    sin_id = copy.deepcopy(arbol)
    for hijo in sin_id.findall("cbc:ID", NS):
        sin_id.remove(hijo)
    errores_id = validar(etree.tostring(sin_id))
    if errores_id:
        ok.append(f"un XML sin cbc:ID es rechazado por el XSD ({len(errores_id)} error/es)")
    else:
        fallos.append("el XSD aceptó un XML sin número de comprobante")

    # 3
    lineas = arbol.findall("cac:InvoiceLine", NS)
    declaradas = arbol.findtext("cbc:LineCountNumeric", namespaces=NS)
    if declaradas is not None and int(declaradas) == len(lineas):
        ok.append(f"LineCountNumeric = {declaradas} coincide con las {len(lineas)} líneas")
    else:
        fallos.append(f"LineCountNumeric {declaradas} != líneas {len(lineas)}")

    # 4
    igv_cabecera = Decimal("0")
    icbper_cabecera = Decimal("0")
    for tax in arbol.findall("cac:TaxTotal", NS):
        for sub in tax.findall("cac:TaxSubtotal", NS):
            codigo = sub.findtext("cac:TaxCategory/cac:TaxScheme/cbc:ID", namespaces=NS)
            monto = decimal(sub.find("cbc:TaxAmount", NS))
            if codigo == "1000":
                igv_cabecera += monto
            elif codigo == "7152":
                icbper_cabecera += monto

    igv_lineas = Decimal("0")
    for linea in lineas:
        for sub in linea.findall("cac:TaxTotal/cac:TaxSubtotal", NS):
            codigo = sub.findtext("cac:TaxCategory/cac:TaxScheme/cbc:ID", namespaces=NS)
            if codigo == "1000":
                igv_lineas += decimal(sub.find("cbc:TaxAmount", NS))
    if igv_cabecera == igv_lineas:
        ok.append(f"IGV de cabecera = suma de líneas = {igv_cabecera}")
    else:
        fallos.append(f"IGV cabecera {igv_cabecera} != suma de líneas {igv_lineas}")

    # 5
    desalineadas = []
    for linea in lineas:
        base = decimal(linea.find("cbc:LineExtensionAmount", NS))
        for sub in linea.findall("cac:TaxTotal/cac:TaxSubtotal", NS):
            codigo = sub.findtext("cac:TaxCategory/cac:TaxScheme/cbc:ID", namespaces=NS)
            if codigo == "1000" and decimal(sub.find("cbc:TaxableAmount", NS)) != base:
                desalineadas.append(linea.findtext("cbc:ID", namespaces=NS))
    if desalineadas:
        fallos.append(f"base imponible distinta de la línea en: {', '.join(desalineadas)}")
    else:
        ok.append("en cada línea, TaxableAmount coincide con LineExtensionAmount")

    # 6
    total = arbol.find("cac:LegalMonetaryTotal", NS)
    valor_venta = decimal(total.find("cbc:LineExtensionAmount", NS))
    con_impuestos = decimal(total.find("cbc:TaxInclusiveAmount", NS))
    a_pagar = decimal(total.find("cbc:PayableAmount", NS))
    suma_lineas = sum(decimal(l.find("cbc:LineExtensionAmount", NS)) for l in lineas)
    if suma_lineas == valor_venta:
        ok.append(f"suma de líneas = {suma_lineas} coincide con el total")
    else:
        fallos.append(f"suma de líneas {suma_lineas} != LineExtensionAmount {valor_venta}")

    # 7
    esperado_con_impuestos = valor_venta + igv_cabecera + icbper_cabecera
    if con_impuestos == esperado_con_impuestos:
        ok.append(
            f"TaxInclusiveAmount = {con_impuestos} incluye IGV e ICBPER "
            f"({valor_venta} + {igv_cabecera} + {icbper_cabecera})"
        )
    else:
        fallos.append(
            f"TaxInclusiveAmount {con_impuestos} != valor + IGV + ICBPER {esperado_con_impuestos}"
        )
    if a_pagar == con_impuestos:
        ok.append(f"PayableAmount = {a_pagar} coincide con el total con impuestos")
    else:
        fallos.append(f"PayableAmount {a_pagar} != TaxInclusiveAmount {con_impuestos}")

    # 7b RUC con dígito verificador (RN-01) en emisor y receptor
    for etiqueta, partido in (
        ("emisor", "cac:AccountingSupplierParty"),
        ("receptor", "cac:AccountingCustomerParty"),
    ):
        nodo = arbol.find(f"{partido}/cac:Party/cac:PartyIdentification/cbc:ID", NS)
        if nodo is None:
            fallos.append(f"falta el documento del {etiqueta}")
            continue
        ruc = (nodo.text or "").strip()
        if _ruc_valido(ruc):
            ok.append(f"RUC del {etiqueta} {ruc} pasa el módulo 11")
        else:
            fallos.append(f"RUC del {etiqueta} {ruc} NO pasa el módulo 11 (RN-01)")

    # 8 control negativo: adulterar el IGV de cabecera debe romper la reconciliación
    adulterado = copy.deepcopy(arbol)
    tax = adulterado.find("cac:TaxTotal", NS)
    tax.find("cbc:TaxAmount", NS).text = "60.00"
    sub = tax.find("cac:TaxSubtotal", NS)
    if sub is not None:
        sub.find("cbc:TaxAmount", NS).text = "60.00"
    igv_adulterado = Decimal("0")
    for t in adulterado.findall("cac:TaxTotal", NS):
        for s in t.findall("cac:TaxSubtotal", NS):
            if s.findtext("cac:TaxCategory/cac:TaxScheme/cbc:ID", namespaces=NS) == "1000":
                igv_adulterado += decimal(s.find("cbc:TaxAmount", NS))
    suma_lineas_ad = sum(decimal(l.find("cbc:LineExtensionAmount", NS)) for l in lineas)
    valor_ad = decimal(adulterado.find("cac:LegalMonetaryTotal", NS).find("cbc:LineExtensionAmount", NS))
    if igv_adulterado != igv_lineas or suma_lineas_ad != valor_ad:
        ok.append("un IGV de cabecera adulterado rompe la reconciliación (control negativo)")
    else:
        fallos.append("la reconciliación NO detectó un IGV adulterado")

    print("=" * 74)
    print(" VALIDACIÓN DEL XML UBL — perfil Invoice 2.1")
    print("=" * 74)
    for linea_ok in ok:
        print(f"  OK    {linea_ok}")
    for linea_fallo in fallos:
        print(f"  FALLA {linea_fallo}")
    print("-" * 74)
    print(f"  {len(ok)} comprobaciones correctas, {len(fallos)} fallos")
    print("=" * 74)
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
