"""Adaptador `IXmlBuilder`: agregado del dominio → clases del XSD oficial → XML UBL 2.1.

No hay plantillas ni concatenación de cadenas:

* las clases vienen del XSD oficial (`generated/`, producidas por `xsdata`);
* el serializador escapa `&`, `<` y `>`;
* el orden de los elementos lo impone el esquema (por eso `cac:TaxTotal` va antes de
  `cac:Item` y `cac:Price` dentro de la línea);
* construir un elemento que el XSD no define es imposible: la clase no existe.

El XML se genera **sin firma**: el adaptador de firma (`IFirmaDigital`) agrega
`ext:UBLExtensions` en la fase 2. El orden del flujo es: generar → **validar contra el
esquema oficial** → firmar → enviar (RN-18).
"""

from __future__ import annotations

from decimal import Decimal

from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.models.datatype import XmlDate, XmlTime

from src.adaptadores.salida.ubl import NAMESPACES, SUNAT, UNECE, catalogo
from src.adaptadores.salida.ubl.generated.common import (
    ubl_common_aggregate_components_2_1 as cac,
)
from src.adaptadores.salida.ubl.generated.common import (
    ubl_common_basic_components_2_1 as cbc,
)
from src.adaptadores.salida.ubl.generated.maindoc.ubl_credit_note_2_1 import CreditNote
from src.adaptadores.salida.ubl.generated.maindoc.ubl_debit_note_2_1 import DebitNote
from src.adaptadores.salida.ubl.generated.maindoc.ubl_invoice_2_1 import Invoice
from src.dominio.catalogos import TipoComprobante, Tributo
from src.dominio.comprobante import Comprobante, Linea
from src.dominio.tributos import CERO, porcentaje_efectivo

_DOS_DECIMALES = Decimal("0.01")
_SEIS_DECIMALES = Decimal("0.000001")


def _d(valor: Decimal) -> Decimal:
    """Cuantiza un importe a 2 decimales para que el XML nunca lleve `1` en lugar de `1.00`."""
    return valor.quantize(_DOS_DECIMALES)


def _valor_unitario(valor: Decimal) -> Decimal:
    """El valor unitario conserva 6 decimales: SUNAT exige que `precio × cantidad` cuadre
    con `LineExtensionAmount`, y con 2 decimales la diferencia se nota (38.14 × 10 ≠ 381.36)."""
    return valor.quantize(_SEIS_DECIMALES)


class GeneradorUblXsdata:
    """Implementa el puerto `IXmlBuilder`."""

    def __init__(self) -> None:
        self._serializador = XmlSerializer(config=SerializerConfig(xml_declaration=True, encoding="UTF-8"))

    # ------------------------------------------------------------------ público
    def generar(self, comprobante: Comprobante) -> bytes:
        """Devuelve el XML UBL 2.1 del comprobante (sin firmar)."""
        documento, raiz = self._documento(comprobante)
        ns_map: dict[str | None, str] = {None: NAMESPACES[raiz]}
        ns_map.update({k: v for k, v in NAMESPACES.items() if k in ("cac", "cbc")})
        xml = self._serializador.render(documento, ns_map=ns_map)
        return xml.encode("utf-8")

    # ------------------------------------------------------------------ documento
    def _documento(self, c: Comprobante):
        comun = dict(
            ublversion_id=cbc.UblversionId(value="2.1"),
            customization_id=cbc.CustomizationId(value="2.0", scheme_agency_name=SUNAT),
            id=cbc.Id(value=c.serie_numero),
            issue_date=cbc.IssueDate(value=XmlDate.from_date(c.fecha_emision)),
            issue_time=cbc.IssueTime(value=XmlTime.from_time(c.hora_emision)),
            # Leyenda 1000: importe total en letras.
            note=[cbc.Note(value=c.monto_en_letras, language_locale_id="1000")],
            document_currency_code=cbc.DocumentCurrencyCode(
                value=c.moneda.value,
                list_id="ISO 4217 Alpha",
                list_name="Currency",
                list_agency_name=UNECE,
            ),
            accounting_supplier_party=self._emisor(c),
            accounting_customer_party=self._cliente(c),
            tax_total=self._tributos_documento(c),
            # Control de consistencia (matriz fila 9): debe coincidir con las líneas.
            line_count_numeric=cbc.LineCountNumeric(value=len(c.lineas)),
        )

        if not c.tipo.es_nota:
            return Invoice(
                **comun,
                invoice_type_code=cbc.InvoiceTypeCode(
                    value=c.tipo.value,
                    list_id=c.tipo_operacion.value,
                    list_agency_name=SUNAT,
                    list_name="Tipo de Documento",
                    list_uri=catalogo("01"),
                ),
                additional_document_reference=self._documentos_legado(c),
                payment_terms=self._forma_pago(c),
                legal_monetary_total=self._total_monetario(c),
                invoice_line=[
                    cac.InvoiceLine(
                        invoiced_quantity=self._cantidad(cbc.InvoicedQuantity, linea.unidad.value, linea.cantidad),
                        **self._linea(c, linea),
                    )
                    for linea in c.lineas
                ],
            ), "Invoice"

        discrepancia = self._discrepancia(c)
        referencia = cac.BillingReference(
            invoice_document_reference=cac.InvoiceDocumentReference(
                id=cbc.Id(value=c.referencia.serie_numero),
                document_type_code=cbc.DocumentTypeCode(
                    value=c.referencia.tipo.value,
                    list_agency_name=SUNAT,
                    list_name="Tipo de Documento",
                    list_uri=catalogo("01"),
                ),
            )
        )
        if c.tipo is TipoComprobante.NOTA_CREDITO:
            return CreditNote(
                **comun,
                discrepancy_response=[discrepancia],
                billing_reference=[referencia],
                legal_monetary_total=self._total_monetario(c),
                credit_note_line=[
                    cac.CreditNoteLine(
                        credited_quantity=self._cantidad(cbc.CreditedQuantity, linea.unidad.value, linea.cantidad),
                        **self._linea(c, linea),
                    )
                    for linea in c.lineas
                ],
            ), "CreditNote"
        return DebitNote(
            **comun,
            discrepancy_response=[discrepancia],
            billing_reference=[referencia],
            requested_monetary_total=cac.RequestedMonetaryTotal(**self._total_monetario(c).__dict__),
            debit_note_line=[
                cac.DebitNoteLine(
                    debited_quantity=self._cantidad(cbc.DebitedQuantity, linea.unidad.value, linea.cantidad),
                    **self._linea(c, linea),
                )
                for linea in c.lineas
            ],
        ), "DebitNote"

    # ------------------------------------------------------------------ partes
    @staticmethod
    def _identificacion(tipo_documento: str, numero: str) -> cac.PartyIdentification:
        return cac.PartyIdentification(
            id=cbc.Id(
                value=numero,
                scheme_id=tipo_documento,
                scheme_name="Documento de Identidad",
                scheme_agency_name=SUNAT,
                scheme_uri=catalogo("06"),
            )
        )

    def _emisor(self, c: Comprobante) -> cac.AccountingSupplierParty:
        e = c.emisor
        return cac.AccountingSupplierParty(
            party=cac.Party(
                party_identification=[self._identificacion("6", str(e.ruc))],
                party_legal_entity=[
                    cac.PartyLegalEntity(
                        registration_name=cbc.RegistrationName(value=e.razon_social),
                        registration_address=cac.RegistrationAddress(
                            id=cbc.Id(
                                value=e.ubigeo,
                                scheme_name="Ubigeos",
                                scheme_agency_name="PE:INEI",
                            ),
                            address_type_code=cbc.AddressTypeCode(
                                value=e.codigo_establecimiento,
                                list_name="Establecimientos anexos",
                                list_agency_name=SUNAT,
                            ),
                            street_name=cbc.StreetName(value=e.direccion) if e.direccion else None,
                        ),
                    )
                ],
            )
        )

    def _cliente(self, c: Comprobante) -> cac.AccountingCustomerParty:
        cl = c.cliente
        direccion = (
            cac.RegistrationAddress(
                id=(
                    cbc.Id(value=cl.ubigeo, scheme_name="Ubigeos", scheme_agency_name="PE:INEI") if cl.ubigeo else None
                ),
                street_name=cbc.StreetName(value=cl.direccion) if cl.direccion else None,
            )
            if (cl.direccion or cl.ubigeo)
            else None
        )
        return cac.AccountingCustomerParty(
            party=cac.Party(
                party_identification=[self._identificacion(cl.documento.tipo.value, cl.documento.numero)],
                party_legal_entity=[
                    cac.PartyLegalEntity(
                        registration_name=cbc.RegistrationName(value=cl.razon_social),
                        registration_address=direccion,
                    )
                ],
            )
        )

    # ------------------------------------------------------------------ tributos
    @staticmethod
    def _esquema(tributo: Tributo) -> cac.TaxScheme:
        return cac.TaxScheme(
            id=cbc.Id(
                value=tributo.value,
                scheme_name="Codigo de tributos",
                scheme_agency_name=SUNAT,
                scheme_uri=catalogo("05"),
            ),
            name=cbc.Name(value=tributo.nombre),
            tax_type_code=cbc.TaxTypeCode(value=tributo.codigo_internacional),
        )

    @staticmethod
    def _categoria(tributo: Tributo) -> cbc.Id:
        return cbc.Id(
            value=tributo.categoria,
            scheme_id="UN/ECE 5305",
            scheme_name="Tax Category Identifier",
            scheme_agency_name=UNECE,
        )

    def _subtotal(
        self,
        tributo: Tributo,
        moneda: str,
        base: Decimal | None,
        monto: Decimal,
        *,
        porcentaje: Decimal | None = None,
        afectacion: str | None = None,
        tier_range: str | None = None,
        per_unit: Decimal | None = None,
        base_medida: tuple[Decimal, str] | None = None,
    ) -> cac.TaxSubtotal:
        categoria = cac.TaxCategory(
            id=self._categoria(tributo),
            percent=cbc.Percent(value=porcentaje) if porcentaje is not None else None,
            tax_exemption_reason_code=(
                cbc.TaxExemptionReasonCode(
                    value=afectacion,
                    list_agency_name=SUNAT,
                    list_name="Afectacion del IGV",
                    list_uri=catalogo("07"),
                )
                if afectacion is not None
                else None
            ),
            tier_range=cbc.TierRange(value=tier_range) if tier_range is not None else None,
            per_unit_amount=(cbc.PerUnitAmount(value=per_unit, currency_id=moneda) if per_unit is not None else None),
            tax_scheme=self._esquema(tributo),
        )
        return cac.TaxSubtotal(
            taxable_amount=(cbc.TaxableAmount(value=base, currency_id=moneda) if base is not None else None),
            tax_amount=cbc.TaxAmount(value=monto, currency_id=moneda),
            base_unit_measure=(
                cbc.BaseUnitMeasure(value=base_medida[0], unit_code=base_medida[1]) if base_medida is not None else None
            ),
            tax_category=categoria,
        )

    def _tributos_documento(self, c: Comprobante) -> list[cac.TaxTotal]:
        """`cac:TaxTotal` del documento: IGV, ISC e ICBPER con sus bases."""
        t, moneda = c.totales, c.moneda.value
        subtotales: list[cac.TaxSubtotal] = []

        if t.op_gravada or t.total_igv:
            # Regla 3277: la base global del IGV es el valor de venta SIN el ISC.
            subtotales.append(
                self._subtotal(
                    Tributo.IGV,
                    moneda,
                    t.op_gravada,
                    t.total_igv,
                    porcentaje=Decimal("18.00") if t.total_igv else Decimal("0.00"),
                    afectacion="10" if t.total_igv else None,
                )
            )
        if t.total_isc:
            # Regla 3108: base × Percent / 100 = monto. El % se deriva cuando el sistema
            # no tiene tasa propia (02 y 03).
            subtotales.append(
                self._subtotal(
                    Tributo.ISC,
                    moneda,
                    t.base_isc,
                    t.total_isc,
                    porcentaje=porcentaje_efectivo(t.total_isc, t.base_isc),
                )
            )
        for monto, tributo in (
            (t.op_exonerada, Tributo.EXONERADO),
            (t.op_inafecta, Tributo.INAFECTO),
            (t.op_exportacion, Tributo.EXPORTACION),
        ):
            if monto:
                subtotales.append(self._subtotal(tributo, moneda, monto, CERO))
        if t.total_icbper:
            # ICBPER es un monto por unidad (RN-07): el XML declara el monto unitario
            # y la cantidad total de bolsas, también en el resumen del documento.
            bolsas = sum((ln.cantidad for ln in c.lineas if ln.aplica_icbper), Decimal("0"))
            subtotales.append(
                self._subtotal(
                    Tributo.ICBPER,
                    moneda,
                    None,
                    t.total_icbper,
                    per_unit=Decimal("0.50"),
                    base_medida=(bolsas, "NIU"),
                )
            )

        return [
            cac.TaxTotal(tax_amount=cbc.TaxAmount(value=t.total_impuestos, currency_id=moneda), tax_subtotal=subtotales)
        ]

    # ------------------------------------------------------------------ totales
    def _total_monetario(self, c: Comprobante) -> cac.LegalMonetaryTotal:
        t, moneda = c.totales, c.moneda.value
        return cac.LegalMonetaryTotal(
            line_extension_amount=cbc.LineExtensionAmount(value=_d(t.valor_venta), currency_id=moneda),
            tax_inclusive_amount=cbc.TaxInclusiveAmount(value=_d(t.importe_total), currency_id=moneda),
            payable_amount=cbc.PayableAmount(value=_d(t.importe_total), currency_id=moneda),
        )

    # ------------------------------------------------------------------ pago
    def _forma_pago(self, c: Comprobante) -> list[cac.PaymentTerms]:
        """Contado: un `PaymentTerms`. Crédito: monto pendiente + una entrada por cuota."""
        if c.forma_pago is None:
            return []
        fp, moneda = c.forma_pago, c.moneda.value
        terminos = [
            cac.PaymentTerms(
                id=cbc.Id(value="FormaPago"),
                payment_means_id=[cbc.PaymentMeansId(value=fp.tipo.value)],
                amount=(cbc.Amount(value=_d(c.totales.importe_total), currency_id=moneda) if fp.cuotas else None),
            )
        ]
        terminos.extend(
            cac.PaymentTerms(
                id=cbc.Id(value="FormaPago"),
                payment_means_id=[cbc.PaymentMeansId(value=f"Cuota{n:03d}")],
                amount=cbc.Amount(value=_d(cuota.monto), currency_id=moneda),
                payment_due_date=cbc.PaymentDueDate(value=XmlDate.from_date(cuota.fecha_vencimiento)),
            )
            for n, cuota in enumerate(fp.cuotas, start=1)
        )
        return terminos

    # ------------------------------------------------------------------ notas
    def _discrepancia(self, c: Comprobante) -> cac.DiscrepancyResponse:
        motivo = c.motivo
        assert motivo is not None and c.referencia is not None  # RN-16 lo garantiza
        es_credito = c.tipo is TipoComprobante.NOTA_CREDITO
        return cac.DiscrepancyResponse(
            reference_id=cbc.ReferenceId(value=c.referencia.serie_numero),
            response_code=cbc.ResponseCode(
                value=motivo.value,
                list_agency_name=SUNAT,
                list_name="Tipo de nota de credito" if es_credito else "Tipo de nota de debito",
                list_uri=catalogo("09" if es_credito else "10"),
            ),
            description=[cbc.Description(value=c.sustento or "Sustento de la nota")],
        )

    def _documentos_legado(self, c: Comprobante) -> list[cac.AdditionalDocumentReference]:
        return [
            cac.AdditionalDocumentReference(
                id=cbc.Id(value=numero),
                document_type_code=cbc.DocumentTypeCode(value="99", list_agency_name=SUNAT),
            )
            for numero in c.documentos_legado
        ]

    # ------------------------------------------------------------------ líneas
    @staticmethod
    def _cantidad(clase, unidad: str, cantidad: Decimal):
        return clase(
            value=cantidad,
            unit_code=unidad,
            unit_code_list_id="UN/ECE rec 20",
            unit_code_list_agency_name=UNECE,
        )

    def _linea(self, c: Comprobante, ln: Linea) -> dict:
        moneda = c.moneda.value
        t = ln.tributos
        subtotales: list[cac.TaxSubtotal] = []

        # ISC: el sistema del catálogo 08 viaja en cbc:TierRange (RN-06).
        if ln.isc is not None:
            subtotales.append(
                self._subtotal(
                    Tributo.ISC,
                    moneda,
                    t.base_isc,
                    t.isc,
                    porcentaje=ln.isc.porcentaje(monto=t.isc, base=t.base_isc),
                    tier_range=ln.isc.sistema.value,
                    per_unit=ln.isc.monto_fijo,
                )
            )
        # IGV o su equivalente según la afectación (catálogo 07): una línea exonerada
        # declara el tributo 9997, no el 1000.
        subtotales.append(
            self._subtotal(
                ln.afectacion.tributo,
                moneda,
                t.base_igv,
                t.igv,
                porcentaje=Decimal("18.00") if ln.afectacion.es_gravada else Decimal("0.00"),
                afectacion=ln.afectacion.value,
            )
        )
        # ICBPER: monto por unidad de medida, no porcentaje (RN-07).
        if ln.aplica_icbper:
            subtotales.append(
                self._subtotal(
                    Tributo.ICBPER,
                    moneda,
                    None,
                    t.icbper,
                    per_unit=Decimal("0.50"),
                    base_medida=(ln.cantidad, ln.unidad.value),
                )
            )

        return dict(
            id=cbc.Id(value=str(ln.numero)),
            line_extension_amount=cbc.LineExtensionAmount(value=_d(t.valor_venta), currency_id=moneda),
            pricing_reference=cac.PricingReference(
                alternative_condition_price=[
                    cac.AlternativeConditionPrice(
                        price_amount=cbc.PriceAmount(value=_d(ln.precio_unitario), currency_id=moneda),
                        price_type_code=cbc.PriceTypeCode(
                            value="01",
                            list_agency_name=SUNAT,
                            list_name="Tipo de Precio",
                            list_uri=catalogo("16"),
                        ),
                    )
                ]
            ),
            tax_total=[
                cac.TaxTotal(
                    tax_amount=cbc.TaxAmount(value=_d(t.isc + t.igv + t.icbper), currency_id=moneda),
                    tax_subtotal=subtotales,
                )
            ],
            item=cac.Item(
                description=[cbc.Description(value=ln.descripcion)],
                sellers_item_identification=(
                    cac.SellersItemIdentification(id=cbc.Id(value=ln.codigo_producto)) if ln.codigo_producto else None
                ),
            ),
            price=cac.Price(price_amount=cbc.PriceAmount(value=_valor_unitario(ln.valor_unitario), currency_id=moneda)),
            allowance_charge=self._descuento(ln, moneda),
        )

    @staticmethod
    def _descuento(ln: Linea, moneda: str) -> list[cac.AllowanceCharge] | None:
        """Descuento por ítem: `cac:AllowanceCharge` con `ChargeIndicator=false` (matriz fila 32).

        `BaseAmount` es el valor ANTES del descuento; `LineExtensionAmount` ya lo descuenta.
        """
        if ln.descuento <= 0:
            return None
        return [
            cac.AllowanceCharge(
                charge_indicator=False,
                amount=cbc.Amount(value=_d(ln.descuento), currency_id=moneda),
                base_amount=cbc.BaseAmount(value=_d(ln.tributos.valor_venta + ln.descuento), currency_id=moneda),
            )
        ]
