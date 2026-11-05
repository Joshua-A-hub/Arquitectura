"""Datos estáticos que simulan la base de datos de ABC Software Corp.

**Mock del sistema.** No hay base de datos real: `src/adaptadores/sqlite_comprobante_repository.py`
(fase 2) leerá y escribirá aquí. Todo dato cumple los esquemas de `specs/contracts/dto/`:
los importes viajan como **string decimal** y el ISC se declara con el **catálogo 08**
(`sistema_isc` = `01` ad valorem, `02` específico, `03` al valor).

Uso: los tests importan `reiniciar()` en un fixture para arrancar siempre en el mismo estado.
"""

from __future__ import annotations

# --- Maestros ---------------------------------------------------------------

DB_EMPRESA: dict = {
    "ruc": "20123456786",
    "razon_social": "ABC SOFTWARE CORP SAC",
    "nombre_comercial": "ABC Abarrotes",
    "ubigeo": "150101",
    "direccion": "AV. COLONIAL 456",
    "regimen_tributario": "REG",
}

DB_CLIENTES: list[dict] = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "tipo_documento": "6",
        "numero_documento": "20512345671",
        "razon_social": "DISTRIBUIDORA SELVA SAC",
        "ubigeo": "150101",
        "direccion": "AV. ARGENTINA 123",
        "email": "compras@diselselva.pe",
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "tipo_documento": "1",
        "numero_documento": "45678912",
        "razon_social": "JUAN PEREZ GOMEZ",
        "ubigeo": "150102",
        "direccion": "JR. LAS BEGONIAS 789",
        "email": "juan.perez@correo.pe",
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "tipo_documento": "0",
        "numero_documento": "0",
        "razon_social": "CLIENTES VARIOS",
        "ubigeo": "150101",
        "direccion": "",
        "email": "",
    },
]

# `afectacion_igv` = catálogo 07 · `sistema_isc` = catálogo 08 (None si no está afecto)
DB_PRODUCTOS: list[dict] = [
    {
        "codigo": "ARR-50KG",
        "descripcion": "SACO DE ARROZ 50KG",
        "unidad_medida": "NIU",
        "precio_unitario": "45.00",
        "afectacion_igv": "10",
        "sistema_isc": None,
        "tasa_isc": "0.00",
        "monto_fijo_isc": None,
        "precio_venta_publico": None,
        "es_bolsa_plastica": False,
        "stock_actual": 120,
    },
    {
        "codigo": "LEC-1L",
        "descripcion": "CAJA DE LECHE 1L",
        "unidad_medida": "BX",
        "precio_unitario": "12.00",
        "afectacion_igv": "20",
        "sistema_isc": None,
        "tasa_isc": "0.00",
        "monto_fijo_isc": None,
        "precio_venta_publico": None,
        "es_bolsa_plastica": False,
        "stock_actual": 80,
    },
    {
        "codigo": "BOL-001",
        "descripcion": "BOLSA PLASTICA RECICLABLE",
        "unidad_medida": "NIU",
        "precio_unitario": "0.50",
        "afectacion_igv": "10",
        "sistema_isc": None,
        "tasa_isc": "0.00",
        "monto_fijo_isc": None,
        "precio_venta_publico": None,
        "es_bolsa_plastica": True,
        "stock_actual": 1000,
    },
    {
        # ISC sistema 01 (ad valorem): cerveza afecta al 25 %.
        "codigo": "CER-620ML",
        "descripcion": "CERVEZA BOTELLA 620 ML",
        "unidad_medida": "NIU",
        "precio_unitario": "8.00",
        "afectacion_igv": "10",
        "sistema_isc": "01",
        "tasa_isc": "25.00",
        "monto_fijo_isc": None,
        "precio_venta_publico": None,
        "es_bolsa_plastica": False,
        "stock_actual": 240,
    },
    {
        # ISC sistema 02 (específico): S/ 1.35 por unidad.
        "codigo": "PIS-750ML",
        "descripcion": "PISCO QUEBRANTA 750 ML",
        "unidad_medida": "NIU",
        "precio_unitario": "53.10",
        "afectacion_igv": "10",
        "sistema_isc": "02",
        "tasa_isc": None,
        "monto_fijo_isc": "1.35",
        "precio_venta_publico": None,
        "es_bolsa_plastica": False,
        "stock_actual": 60,
    },
    {
        # ISC sistema 03 (al valor / precio de venta al público).
        "codigo": "GAS-3L",
        "descripcion": "GASEOSA 3 L",
        "unidad_medida": "NIU",
        "precio_unitario": "10.62",
        "afectacion_igv": "10",
        "sistema_isc": "03",
        "tasa_isc": "17.00",
        "monto_fijo_isc": None,
        "precio_venta_publico": "12.50",
        "es_bolsa_plastica": False,
        "stock_actual": 96,
    },
]

# --- Estado transaccional ---------------------------------------------------

DB_CORRELATIVOS: dict[str, int] = {"F001": 0, "B001": 0}
DB_COMPROBANTES: list[dict] = []
DB_NOTAS: list[dict] = []

# Fichas del sistema legado (fecha, ingreso, salida, producto, nro_documento)
DB_FICHAS_LEGADO: list[dict] = [
    {
        "id_ficha": "F-0001",
        "fecha": "2026-05-01",
        "ingreso": "10 cajas",
        "salida": None,
        "producto": "arroz 50 kg",
        "nro_documento": "INT-8891",
        "origen_archivo": "almacen_2026.xlsx",
    },
    {
        "id_ficha": "F-0002",
        "fecha": "2026-05-03",
        "ingreso": None,
        "salida": "5 cajas",
        "producto": "CAJA DE LECHE 1L",
        "nro_documento": "INT-8892",
        "origen_archivo": "almacen_2026.xlsx",
    },
    {
        "id_ficha": "F-0003",
        "fecha": "2026-05-04",
        "ingreso": "2 sacos",
        "salida": "2 sacos",
        "producto": "producto desconocido",
        "nro_documento": "",
        "origen_archivo": "almacen_2026.xlsx",
    },
]


def reiniciar() -> None:
    """Devuelve el estado a cero. La usan los tests para ser independientes."""
    DB_COMPROBANTES.clear()
    DB_NOTAS.clear()
    DB_CORRELATIVOS.clear()
    DB_CORRELATIVOS.update({"F001": 0, "B001": 0})


def buscar_cliente(numero_documento: str) -> dict | None:
    for cliente in DB_CLIENTES:
        if cliente["numero_documento"] == numero_documento:
            return cliente
    return None


def buscar_producto(codigo: str) -> dict | None:
    for producto in DB_PRODUCTOS:
        if producto["codigo"] == codigo:
            return producto
    return None
