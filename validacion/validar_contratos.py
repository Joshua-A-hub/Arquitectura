"""Validador de los contratos de la entrega (sin dependencias externas).

Comprueba tres cosas:
  1. Que todos los JSON Schema de `specs/contracts/dto/` sean JSON válido y tengan $schema y type.
  2. Que el ejemplo válido cumpla su esquema y el ejemplo inválido NO lo cumpla.
  3. Que el OpenAPI (`facturacion-api.yaml`) tenga la estructura mínima y que todos los
     `$ref: '#/components/schemas/X'` apunten a un esquema declarado.

Uso:
    python validacion/validar_contratos.py
Código de salida 0 = todo bien, 1 = hay errores.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DIR_DTO = RAIZ / "specs" / "contracts" / "dto"
RUTA_OPENAPI = RAIZ / "specs" / "contracts" / "facturacion-api.yaml"


# --------------------------------------------------------------------------- #
# Validador mínimo de JSON Schema (subconjunto suficiente para estos contratos)
# --------------------------------------------------------------------------- #

TIPOS = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


def _tipo_ok(valor, tipo: str) -> bool:
    if tipo == "integer":
        return isinstance(valor, int) and not isinstance(valor, bool)
    if tipo == "number":
        return isinstance(valor, (int, float)) and not isinstance(valor, bool)
    if tipo == "boolean":
        return isinstance(valor, bool)
    esperado = TIPOS.get(tipo)
    if esperado is None:
        return True
    return isinstance(valor, esperado)


def validar(instancia, esquema: dict, ruta: str = "$", raiz: dict | None = None) -> list[str]:
    """Devuelve la lista de errores encontrados (vacía = válido)."""
    raiz = raiz or esquema
    errores: list[str] = []

    # $ref local (#/definitions/...)
    if "$ref" in esquema:
        destino = _resolver_ref(esquema["$ref"], raiz)
        if destino is None:
            return [f"{ruta}: $ref no resoluble {esquema['$ref']}"]
        return validar(instancia, destino, ruta, raiz)

    # allOf / if-then
    for sub in esquema.get("allOf", []):
        errores += validar(instancia, sub, ruta, raiz)
    if "if" in esquema and "then" in esquema:
        if not validar(instancia, esquema["if"], ruta, raiz):
            errores += validar(instancia, esquema["then"], ruta, raiz)

    tipo = esquema.get("type")
    if isinstance(tipo, list):
        if not any(_tipo_ok(instancia, t) for t in tipo):
            errores.append(f"{ruta}: se esperaba uno de {tipo}")
            return errores
    elif tipo and not _tipo_ok(instancia, tipo):
        errores.append(f"{ruta}: se esperaba {tipo}, llegó {type(instancia).__name__}")
        return errores

    if "enum" in esquema and instancia not in esquema["enum"]:
        errores.append(f"{ruta}: {instancia!r} no está en {esquema['enum']}")

    if "const" in esquema and instancia != esquema["const"]:
        errores.append(f"{ruta}: se esperaba el valor constante {esquema['const']!r}")

    if isinstance(instancia, str):
        if "minLength" in esquema and len(instancia) < esquema["minLength"]:
            errores.append(f"{ruta}: longitud {len(instancia)} < minLength {esquema['minLength']}")
        if "maxLength" in esquema and len(instancia) > esquema["maxLength"]:
            errores.append(f"{ruta}: longitud {len(instancia)} > maxLength {esquema['maxLength']}")
        if "pattern" in esquema and not re.fullmatch(esquema["pattern"], instancia):
            errores.append(f"{ruta}: {instancia!r} no cumple pattern {esquema['pattern']!r}")
        formato = esquema.get("format")
        if formato == "uuid" and not re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", instancia
        ):
            errores.append(f"{ruta}: {instancia!r} no es un UUID")
        if formato == "date" and not _fecha_valida(instancia):
            errores.append(f"{ruta}: {instancia!r} no es una fecha ISO válida")
        if formato == "date-time" and not _fecha_hora_valida(instancia):
            errores.append(f"{ruta}: {instancia!r} no es un date-time ISO válido")
        if formato == "email" and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", instancia):
            errores.append(f"{ruta}: {instancia!r} no es un correo válido")

    if isinstance(instancia, (int, float)) and not isinstance(instancia, bool):
        exclusivo = esquema.get("exclusiveMinimum")
        if isinstance(exclusivo, (int, float)) and not isinstance(exclusivo, bool):
            # draft-07: exclusiveMinimum numérico
            if instancia <= exclusivo:
                errores.append(f"{ruta}: debe ser > {exclusivo}")
        elif "minimum" in esquema:
            if exclusivo is True:
                if instancia <= esquema["minimum"]:
                    errores.append(f"{ruta}: debe ser > {esquema['minimum']}")
            elif instancia < esquema["minimum"]:
                errores.append(f"{ruta}: debe ser >= {esquema['minimum']}")
        if "maximum" in esquema and instancia > esquema["maximum"]:
            errores.append(f"{ruta}: debe ser <= {esquema['maximum']}")

    if isinstance(instancia, dict):
        for campo in esquema.get("required", []):
            if campo not in instancia:
                errores.append(f"{ruta}: falta el campo obligatorio '{campo}'")
        propiedades = esquema.get("properties", {})
        for clave, valor in instancia.items():
            if clave in propiedades:
                errores += validar(valor, propiedades[clave], f"{ruta}.{clave}", raiz)
            elif esquema.get("additionalProperties") is False:
                errores.append(f"{ruta}: campo no permitido '{clave}'")

    if isinstance(instancia, list):
        if "minItems" in esquema and len(instancia) < esquema["minItems"]:
            errores.append(f"{ruta}: {len(instancia)} elementos < minItems {esquema['minItems']}")
        if "maxItems" in esquema and len(instancia) > esquema["maxItems"]:
            errores.append(f"{ruta}: {len(instancia)} elementos > maxItems {esquema['maxItems']}")
        if "items" in esquema:
            for indice, elemento in enumerate(instancia):
                errores += validar(elemento, esquema["items"], f"{ruta}[{indice}]", raiz)

    return errores


def _fecha_valida(texto: str) -> bool:
    from datetime import date

    try:
        anio, mes, dia = (int(p) for p in texto.split("-"))
        date(anio, mes, dia)
        return True
    except (ValueError, TypeError):
        return False


def _fecha_hora_valida(texto: str) -> bool:
    from datetime import datetime

    candidato = texto.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(candidato)
        return True
    except ValueError:
        return False


def _resolver_ref(ref: str, raiz: dict):
    if not ref.startswith("#/"):
        return None
    actual = raiz
    for parte in ref[2:].split("/"):
        if not isinstance(actual, dict) or parte not in actual:
            return None
        actual = actual[parte]
    return actual


# --------------------------------------------------------------------------- #
# Comprobaciones
# --------------------------------------------------------------------------- #

def main() -> int:
    fallos: list[str] = []
    ok: list[str] = []

    esquemas = sorted(DIR_DTO.glob("*.schema.json"))
    if not esquemas:
        print("ERROR: no se encontraron esquemas en", DIR_DTO)
        return 1

    for ruta in esquemas:
        try:
            contenido = json.loads(ruta.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            fallos.append(f"{ruta.name}: JSON inválido ({error})")
            continue
        if "$schema" not in contenido or "type" not in contenido:
            fallos.append(f"{ruta.name}: falta $schema o type")
            continue
        ok.append(f"{ruta.name}: esquema válido")

    esquema_comprobante = json.loads(
        (DIR_DTO / "comprobante-create.schema.json").read_text(encoding="utf-8")
    )
    ejemplo_valido = json.loads((DIR_DTO / "ejemplo-comprobante.json").read_text(encoding="utf-8"))
    ejemplo_invalido = json.loads(
        (DIR_DTO / "ejemplo-comprobante-invalido.json").read_text(encoding="utf-8")
    )

    errores_valido = validar(ejemplo_valido, esquema_comprobante)
    if errores_valido:
        fallos.append("El ejemplo VÁLIDO no cumple el esquema: " + "; ".join(errores_valido[:3]))
    else:
        ok.append("ejemplo-comprobante.json cumple comprobante-create.schema.json")

    errores_invalido = validar(ejemplo_invalido, esquema_comprobante)
    if not errores_invalido:
        fallos.append("El ejemplo INVÁLIDO pasó la validación (el esquema es demasiado laxo)")
    else:
        ok.append(
            f"ejemplo-comprobante-invalido.json detectado con {len(errores_invalido)} errores "
            f"(p. ej.: {errores_invalido[0]})"
        )

    # Contrato de salida: la respuesta también está validada
    esquema_respuesta = json.loads(
        (DIR_DTO / "comprobante-response.schema.json").read_text(encoding="utf-8")
    )
    ejemplo_respuesta = json.loads(
        (DIR_DTO / "ejemplo-comprobante-response.json").read_text(encoding="utf-8")
    )
    errores_respuesta = validar(ejemplo_respuesta, esquema_respuesta)
    if errores_respuesta:
        fallos.append(
            "El ejemplo de RESPUESTA no cumple su esquema: " + "; ".join(errores_respuesta[:3])
        )
    else:
        ok.append("ejemplo-comprobante-response.json cumple comprobante-response.schema.json")

    # OpenAPI: estructura mínima y coherencia de $ref
    texto = RUTA_OPENAPI.read_text(encoding="utf-8")
    for clave in ("openapi:", "info:", "paths:", "components:", "schemas:"):
        if clave not in texto:
            fallos.append(f"OpenAPI: falta la sección '{clave}'")
    if "openapi:" in texto and "paths:" in texto and "components:" in texto:
        ok.append("OpenAPI: estructura mínima presente")

    # Si PyYAML está disponible se parsea de verdad (detecta duplicados y errores de sintaxis)
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None

    if yaml is not None:
        try:
            documento = yaml.safe_load(texto)
        except yaml.YAMLError as error:
            documento = None
            fallos.append(f"OpenAPI: el YAML no parsea ({str(error)[:80]})")
        if isinstance(documento, dict):
            rutas_reales = documento.get("paths", {})
            esquemas_reales = documento.get("components", {}).get("schemas", {})
            parametros = documento.get("components", {}).get("parameters", {})
            respuestas = documento.get("components", {}).get("responses", {})
            ok.append(f"OpenAPI: YAML parsea correctamente ({len(rutas_reales)} rutas)")

            # 1. Todo $ref debe apuntar a algo declarado
            referencias = set(re.findall(r"#/components/([a-z]+)/([A-Za-z0-9_]+)", texto))
            declarado = {
                "schemas": set(esquemas_reales),
                "parameters": set(parametros),
                "responses": set(respuestas),
            }
            huerfanas = sorted(
                f"{seccion}/{nombre}"
                for seccion, nombre in referencias
                if seccion in declarado and nombre not in declarado[seccion]
            )
            if huerfanas:
                fallos.append(f"OpenAPI: $ref sin destino -> {', '.join(huerfanas)}")
            else:
                ok.append(
                    f"OpenAPI: {len(referencias)} referencias resueltas "
                    f"({len(esquemas_reales)} esquemas, {len(parametros)} parámetros)"
                )

            # 2. Toda operación debe declarar al menos una respuesta
            sin_respuesta = []
            for ruta, item in rutas_reales.items():
                for metodo, operacion in item.items():
                    if metodo in ("get", "post", "put", "patch", "delete") and not operacion.get(
                        "responses"
                    ):
                        sin_respuesta.append(f"{metodo.upper()} {ruta}")
            if sin_respuesta:
                fallos.append(f"OpenAPI: operaciones sin responses -> {', '.join(sin_respuesta)}")
            else:
                ok.append("OpenAPI: todas las operaciones declaran respuestas")

            # 3. Los DTO de entrada no deben aceptar campos que el dominio calcula
            entrada = esquemas_reales.get("ComprobanteCreate", {}).get("properties", {})
            prohibidos = {"totales", "id", "estado", "hash_xml", "serie_numero"} & set(entrada)
            if prohibidos:
                fallos.append(f"OpenAPI: el DTO de entrada acepta campos calculados {prohibidos}")
            else:
                ok.append("OpenAPI: el DTO de entrada no acepta totales, id, estado ni serie_numero")
    else:
        # Sin PyYAML no se puede validar el documento: se comprueba lo verificable por texto
        referencias = set(re.findall(r"#/components/schemas/([A-Za-z0-9_]+)", texto))
        definidos = set(
            re.findall(r"^    ([A-Za-z0-9_]+):\s*$", texto, flags=re.MULTILINE)
        )
        huerfanas = sorted(referencias - definidos)
        if huerfanas:
            fallos.append(f"OpenAPI: $ref sin esquema -> {', '.join(huerfanas)}")
        else:
            ok.append(
                f"OpenAPI: {len(referencias)} referencias resueltas por análisis de texto "
                "(instala pyyaml para validar la estructura completa)"
            )

    # Informe
    print("=" * 72)
    print(" VALIDACIÓN DE CONTRATOS — Facturación Electrónica ABC Software Corp")
    print("=" * 72)
    for linea in ok:
        print(f"  OK    {linea}")
    for linea in fallos:
        print(f"  FALLA {linea}")
    print("-" * 72)
    print(f"  {len(ok)} comprobaciones correctas, {len(fallos)} fallos")
    print("=" * 72)
    if fallos:
        return 1
    print("  RESULTADO: los contratos son coherentes y los ejemplos se comportan")
    print("  como se espera (el válido pasa, el inválido se rechaza).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
