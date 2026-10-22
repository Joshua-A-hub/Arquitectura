"""Verifica la entrega completa con un solo comando.

Ejecuta las pruebas de contrato, la validación del XML contra el XSD, y comprobaciones de
integridad del repositorio. Devuelve 0 si todo pasa.

Uso:
    python validacion/verificar_entrega.py
"""

from __future__ import annotations

import contextlib
import io
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DIR_DTO = RAIZ / "specs" / "contracts" / "dto"
DIR_DOCS = RAIZ / "docs" / "arquitectura"

resultados: list[tuple[bool, str, str]] = []


def registrar(ok: bool, nombre: str, detalle: str = "") -> None:
    resultados.append((ok, nombre, detalle))


def ejecutar_validador(ruta: Path, nombre: str) -> None:
    """Importa y ejecuta un validador, capturando su salida."""
    sys.path.insert(0, str(ruta.parent))
    try:
        modulo = __import__(ruta.stem)
    except ImportError as error:  # falta lxml u otra dependencia
        registrar(False, nombre, f"no ejecutable: {error}")
        return
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        codigo = modulo.main()
    salida = buffer.getvalue()
    resumen = ""
    for linea in salida.splitlines():
        if "comprobaciones" in linea:
            resumen = linea.strip()
    registrar(codigo == 0, nombre, resumen)


def verificar_contratos() -> None:
    ejecutar_validador(RAIZ / "validacion" / "validar_contratos.py", "Contratos (schemas + OpenAPI)")


def verificar_xml() -> None:
    ejecutar_validador(RAIZ / "validacion" / "validar_xml_ubl.py", "XML UBL contra su XSD")


def verificar_enlaces() -> None:
    documentos = list(RAIZ.rglob("*.md"))
    rotos: list[str] = []
    for documento in documentos:
        texto = documento.read_text(encoding="utf-8")
        for destino in re.findall(r"\]\(([^)]+)\)", texto):
            if destino.startswith(("http", "#")):
                continue
            limpio = destino.split("#")[0].strip()
            if limpio and not (documento.parent / limpio).exists():
                rotos.append(f"{documento.name}→{destino}")
    registrar(not rotos, "Enlaces internos", f"{len(documentos)} documentos, {len(rotos)} roto/s")


def verificar_codificacion() -> None:
    extensiones = {".md", ".json", ".yaml", ".svg", ".py", ".xml", ".xsd", ".txt"}
    con_bom = [
        f.name
        for f in RAIZ.rglob("*")
        if f.suffix.lower() in extensiones and f.read_bytes().startswith(b"\xef\xbb\xbf")
    ]
    registrar(not con_bom, "Codificación sin BOM", f"{len(con_bom)} archivo/s con BOM")


def contar(patron: str, ruta: Path) -> int:
    return len(re.findall(patron, ruta.read_text(encoding="utf-8"), flags=re.MULTILINE))


def verificar_cifras() -> None:
    """Las cifras que los documentos declaran deben coincidir con lo que contienen."""
    esperado = {
        "cruces de la matriz": (RAIZ / "docs/arquitectura/04-matriz-trazabilidad-normativa.md",
                                r"^\|\s*\d+\s*\|", 59),
        "campos de la tabla de match": (RAIZ / "docs/arquitectura/08-tabla-match-sunat-ubl.md",
                                        r"^\|\s*\d+\s*\|", 47),
        "reglas de negocio": (RAIZ / "specs/domain/reglas-negocio.md", r"^### RN-\d+", 24),
        "escenarios Gherkin": (RAIZ / "specs/features/casos-de-uso.md", r"```gherkin", 10),
        "catálogos SUNAT": (RAIZ / "specs/contracts/catalogs/catalogos-sunat.md", r"^## Catálogo", 9),
    }
    problemas = []
    for nombre, (ruta, patron, valor) in esperado.items():
        if not ruta.exists():
            problemas.append(f"falta {ruta.name}")
            continue
        medido = contar(patron, ruta)
        if medido != valor:
            problemas.append(f"{nombre}: {medido} != {valor}")
    registrar(not problemas, "Cifras declaradas", "; ".join(problemas) or "5 cifras coinciden")


def verificar_entregables() -> None:
    """Los cuatro entregables y la memoria deben existir."""
    requeridos = {
        "E1 modelo": RAIZ / "specs/domain/modelo-dominio.md",
        "E1 schemas": DIR_DTO / "comprobante-create.schema.json",
        "E2 diagramas": DIR_DOCS / "01-mvc-capas.svg",
        "E2 hexagonal": DIR_DOCS / "02-hexagonal.svg",
        "E3 contrato": RAIZ / "specs/contracts/facturacion-api.yaml",
        "E4 matriz": DIR_DOCS / "04-matriz-trazabilidad-normativa.md",
        "Memoria": RAIZ / "MEMORIA-TECNICA.docx",
    }
    faltan = [nombre for nombre, ruta in requeridos.items() if not ruta.exists()]
    registrar(not faltan, "Artefactos entregables", f"{len(requeridos) - len(faltan)}/{len(requeridos)} presentes")


def verificar_referencias_reglas() -> None:
    """Toda regla citada (RN-xx) debe existir en el catálogo de reglas."""
    catalogo = RAIZ / "specs/domain/reglas-negocio.md"
    definidas = set(re.findall(r"^### (RN-\d{2})", catalogo.read_text(encoding="utf-8"), re.M))
    citadas: set[str] = set()
    for documento in RAIZ.rglob("*.md"):
        citadas |= set(re.findall(r"RN-\d{2}", documento.read_text(encoding="utf-8")))
    huerfanas = sorted(citadas - definidas)
    detalle = f"{len(citadas)} reglas citadas, todas definidas"
    if huerfanas:
        detalle = f"citan reglas inexistentes: {', '.join(huerfanas)}"
    registrar(not huerfanas, "Referencias a reglas", detalle)


def verificar_figuras() -> None:
    svgs = list(DIR_DOCS.glob("*.svg"))
    sin_png = [s.name for s in svgs if not s.with_suffix(".png").exists()]
    registrar(not sin_png, "Figuras con vista previa PNG", f"{len(svgs)} SVG, {len(sin_png)} sin PNG")


def main() -> int:
    for prueba in (
        verificar_contratos,
        verificar_xml,
        verificar_enlaces,
        verificar_codificacion,
        verificar_cifras,
        verificar_referencias_reglas,
        verificar_entregables,
        verificar_figuras,
    ):
        try:
            prueba()
        except Exception as error:  # una prueba rota no debe ocultar las demás
            registrar(False, prueba.__name__, f"excepción: {error}")

    correctas = sum(1 for ok, _, _ in resultados if ok)
    print("=" * 78)
    print(" VERIFICACIÓN DE LA ENTREGA — Facturación Electrónica ABC Software Corp")
    print("=" * 78)
    for ok, nombre, detalle in resultados:
        marca = "OK   " if ok else "FALLA"
        print(f"  {marca} {nombre:34s} {detalle}")
    print("-" * 78)
    print(f"  {correctas}/{len(resultados)} comprobaciones correctas")
    print("=" * 78)
    if correctas == len(resultados):
        print("  RESULTADO: la entrega es coherente y verificable.")
        print("  (No prueba que el sistema funcione: eso exige la fase 2 de implementación.)")
        return 0
    print("  RESULTADO: hay fallos; revisa las líneas FALLA.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
