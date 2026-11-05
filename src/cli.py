"""CLI del proyecto (segundo adaptador de entrada).

Es la prueba práctica de que el núcleo no depende del HTTP: este comando usa el mismo
caso de uso (generar el XML del comprobante) que la API.

    python -m src.cli generar-xml specs/contracts/dto/ejemplo-comprobante.json --salida out
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, time
from decimal import Decimal
from pathlib import Path

from src.adapters.outbound.ubl.generador import GeneradorUblXsdata
from src.adapters.outbound.ubl.validador import ValidadorXsd
from src.domain.catalogos import (
    AfectacionIGV,
    Moneda,
    SistemaISC,
    TipoComprobante,
    TipoDocumentoIdentidad,
    TipoFormaPago,
    TipoOperacion,
    UnidadMedida,
)
from src.domain.comprobante import Cliente, Comprobante, Cuota, Emisor, FormaPago, Linea
from src.domain.errores import ErrorDominio
from src.domain.tributos import ConfiguracionISC
from src.domain.valores import RUC, Correlativo, DocumentoIdentidad, Serie

RAIZ = Path(__file__).resolve().parents[1]


def _linea(datos: dict) -> Linea:
    isc = None
    if datos.get("sistema_isc"):
        isc = ConfiguracionISC(
            SistemaISC(datos["sistema_isc"]),
            tasa=Decimal(datos["tasa_isc"]) if datos.get("tasa_isc") else None,
            monto_fijo=Decimal(datos["monto_fijo_isc"]) if datos.get("monto_fijo_isc") else None,
            precio_venta_publico=(
                Decimal(datos["precio_venta_publico"]) if datos.get("precio_venta_publico") else None
            ),
        )
    return Linea.calcular(
        numero=datos["numero_linea"],
        descripcion=datos["descripcion"],
        unidad=UnidadMedida(datos["unidad_medida"]),
        cantidad=datos["cantidad"],
        precio_unitario=datos["precio_unitario"],
        afectacion=AfectacionIGV(datos["afectacion_igv"]),
        codigo_producto=datos.get("producto_codigo"),
        descuento=datos.get("descuento", "0.00"),
        isc=isc,
        aplica_icbper=bool(datos.get("aplica_icbper")),
    )


def construir(datos: dict) -> Comprobante:
    """Traduce la solicitud (formato de `specs/contracts/dto/`) al agregado del dominio."""
    emisor = Emisor(
        ruc=RUC("20123456786"),
        razon_social="ABC SOFTWARE CORP SAC",
        direccion="AV. COLONIAL 456",
    )
    cliente = datos["cliente"]
    forma_pago = None
    if datos.get("forma_pago"):
        cuotas = tuple(
            Cuota(Decimal(c["monto"]), date.fromisoformat(c["fecha_vencimiento"])) for c in datos.get("cuotas", [])
        )
        forma_pago = FormaPago(TipoFormaPago(datos["forma_pago"]), cuotas)

    return Comprobante(
        tipo=TipoComprobante(datos["tipo"]),
        serie=Serie(datos["serie"]),
        correlativo=Correlativo(int(datos.get("correlativo", 1))),
        fecha_emision=date.fromisoformat(datos["fecha_emision"]),
        hora_emision=time.fromisoformat(datos.get("hora_emision", "09:00:00")),
        emisor=emisor,
        cliente=Cliente(
            DocumentoIdentidad(TipoDocumentoIdentidad(cliente["tipo_documento"]), cliente["numero_documento"]),
            cliente["razon_social"],
            direccion=cliente.get("direccion", ""),
            ubigeo=cliente.get("ubigeo", ""),
        ),
        lineas=tuple(_linea(item) for item in datos["detalle"]),
        moneda=Moneda(datos.get("moneda", "PEN")),
        tipo_operacion=TipoOperacion(datos.get("tipo_operacion", "0101")),
        forma_pago=forma_pago,
    )


def generar_xml(entrada: Path, salida: Path) -> int:
    """Genera el XML, lo valida contra el esquema oficial y lo escribe."""
    solicitud = json.loads(entrada.read_text(encoding="utf-8"))
    comprobante = construir(solicitud)
    xml = GeneradorUblXsdata().generar(comprobante)

    validador = ValidadorXsd()
    errores = validador.validar(xml, comprobante.tipo)
    if errores:
        print("El XML no valida contra el esquema oficial:", file=sys.stderr)
        for error in errores[:10]:
            print(f"  - {error}", file=sys.stderr)
        return 1

    salida.mkdir(parents=True, exist_ok=True)
    destino = salida / f"{comprobante.serie_numero}.xml"
    destino.write_bytes(xml)
    resumen = comprobante.resumen()
    print(
        f"OK  {destino}  [{comprobante.tipo.name}]  "
        f"total {resumen['importe_total']} {resumen['moneda']}  "
        f"(valor {resumen['valor_venta']} + IGV {resumen['igv']})"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="src.cli", description="Herramientas de ABC Software Corp")
    sub = parser.add_subparsers(dest="comando", required=True)

    generar = sub.add_parser("generar-xml", help="genera el XML UBL 2.1 de una solicitud JSON")
    generar.add_argument("entrada", type=Path, help="archivo JSON con la solicitud de emisión")
    generar.add_argument("--salida", type=Path, default=RAIZ / "out", help="carpeta de salida")

    args = parser.parse_args(argv)
    try:
        if args.comando == "generar-xml":
            return generar_xml(args.entrada, args.salida)
    except (ErrorDominio, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
