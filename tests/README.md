# Tests

En Spec-Driven Development los tests se organizan por **qué validan**, no por carpeta del código.
Aquí la unidad de organización es la **regla de negocio**: cada archivo de `reglas/` implementa una
regla `RN-xx` y cita la fila de la matriz que verifica.

```text
tests/
├── unit/
│   ├── reglas/                     una regla por archivo (trazabilidad RN → matriz → prueba)
│   │   ├── test_rn01_ruc.py
│   │   ├── test_rn02_documento_receptor.py
│   │   ├── test_rn03_integridad_partes.py
│   │   ├── test_rn04_valor_unitario.py
│   │   ├── test_rn05_igv.py
│   │   ├── test_rn06_isc_catalogo_08.py
│   │   ├── test_rn07_icbper.py
│   │   ├── test_rn08_redondeo.py
│   │   ├── test_rn09_totales.py
│   │   ├── test_rn10_serie.py
│   │   ├── test_rn11_correlativo.py
│   │   ├── test_rn13_fecha_emision.py
│   │   ├── test_rn14_detalle.py
│   │   ├── test_rn16_notas_y_cuotas.py
│   │   ├── test_rn18_conformidad_esquema.py
│   │   ├── test_rn23_documento_legado.py
│   │   ├── test_rn25_forma_pago.py
│   │   ├── test_descuento_item.py       (matriz fila 32)
│   │   └── test_leyenda_1000.py         (matriz fila 6)
│   └── generacion_xml/             forma del documento, no reglas
│       ├── escenarios.py              escenarios del dominio (sin HTTP ni base de datos)
│       ├── test_estructura_xml.py  raíz, namespaces, catálogos 01/02/03/51, orden del XSD
│       ├── test_regresion_golden.py el XML no cambia sin querer
│       └── esperados/              6 XML propios (factura del contrato, ISC, exportación, boleta, NC, migrada)
├── acceptance/                     escenarios Gherkin de specs/features/ (fase 2)
├── integration/                    interacción entre adaptadores (fase 2)
├── mocks/mock_db.py                datos estáticos que simulan la persistencia
└── README.md                       esta guía
```

## Estado

| Nivel | Estado |
|---|---|
| `unit/reglas` | **implementado**: 19 archivos, una regla `RN-xx` por archivo |
| `unit/generacion_xml` | **implementado**: estructura del UBL + regresión contra `esperados/` |
| `acceptance` | especificado (Gherkin), se implementa cuando exista la API |
| `integration` | especificado, requiere repositorio y OSE |

Total: **147 pruebas** (`pytest tests/unit`).

## Cómo se ejecutan

```powershell
pip install -r requirements-dev.txt
pytest tests/unit -q
```

En el entorno de este repositorio las dependencias viven en `_tools/` (no se versionan):

```powershell
$env:PYTHONPATH = "$PWD\_tools\deps;$PWD\_tools;$PWD"
pytest tests/unit -q
```

## Qué garantiza cada grupo

**`reglas/`** — una prueba por regla, con su docstring:

1. **RN-01** RUC con módulo 11 · **RN-02** documento del receptor (catálogo 06) · **RN-03** partes.
2. **RN-04** valor unitario sin IGV · **RN-05** IGV 18 % y reglas SUNAT 3108/3277 · **RN-06** ISC
   con los tres sistemas del catálogo 08 · **RN-07** ICBPER · **RN-08** redondeo · **RN-09** totales.
3. **RN-10** serie alfanumérica · **RN-11** correlativo · **RN-13** fecha · **RN-14** detalle ·
   **RN-16** notas y cuotas · **RN-23** documento del legado · **RN-25** forma de pago.
4. **RN-18** conformidad con el esquema oficial de OASIS (los 6 escenarios).

**`generacion_xml/`** — la *forma* del documento: elemento raíz según el tipo, namespaces, catálogos
de cabecera, moneda en cada importe, orden de los elementos que impone el XSD, determinismo y
regresión byte a byte contra `esperados/`.

## Regenerar los XML de referencia

Solo cuando el cambio sea intencional (y después de corregir las reglas):

```powershell
$env:ACTUALIZAR_ESPERADOS="1"; pytest tests/unit/generacion_xml; Remove-Item Env:ACTUALIZAR_ESPERADOS
```
