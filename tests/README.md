# Tests

En Spec-Driven Development los tests se organizan por **qué validan**, no por carpeta del código.

```text
tests/
├── unit/
│   ├── generacion_xml/     Taller 2: generación del XML UBL (lo que se evalúa)
│   │   ├── fabrica.py      escenarios del dominio (sin HTTP ni base de datos)
│   │   ├── test_*.py       98 pruebas de generación
│   │   └── esperados/      XML de referencia ("golden files")
│   └── test_dominio.py     44 pruebas de cálculo y reglas
├── acceptance/             escenarios Gherkin de specs/features/ (fase 2)
├── integration/            interacción entre adaptadores (fase 2)
├── mocks/mock_db.py        datos estáticos que simulan la persistencia
└── README.md               esta guía
```

## Estado

| Nivel | Estado |
|---|---|
| `unit/generacion_xml` | **implementado**: 98 pruebas de generación + conformidad con el XSD oficial |
| `unit/test_dominio.py` | **implementado**: 44 pruebas (RUC, serie, IGV, ISC, ICBPER, letras, cuotas) |
| `acceptance` | especificado (Gherkin), se implementa cuando exista la API |
| `integration` | especificado, requiere repositorio y OSE |

## Cómo se ejecutan

```powershell
pip install -r requirements-dev.txt
pytest tests/unit -q
```

En el entorno de este repositorio las dependencias viven en `_tools/` (no se versionan), así que se
ejecuta con `PYTHONPATH` apuntando ahí:

```powershell
$env:PYTHONPATH = "$PWD\_tools\deps;$PWD\_tools;$PWD"
pytest tests/unit -q
```

## Qué garantizan las pruebas de generación

1. **Estructura**: raíz, orden de los elementos que impone el XSD y namespaces.
2. **Datos**: `serie_numero` → `cbc:ID`, catálogos 01/02/03/05/06/07/08 en su elemento.
3. **Cálculo**: IGV, ISC de los tres sistemas, ICBPER, cuadre de totales por línea y por documento.
4. **Conformidad**: los 8 escenarios validan contra `UBL-Invoice-2.1.xsd` (y NC/ND contra sus XSD).
5. **Regresión**: el XML no cambia sin que se note (comparación byte a byte con `esperados/`).
6. **Robustez**: determinismo y escape de `&`, `<`, `>`, `"`, `'`, `Ñ`, `€`.

Regenerar los XML de referencia cuando el cambio es intencional:

```powershell
$env:ACTUALIZAR_ESPERADOS="1"; pytest tests/unit/generacion_xml; Remove-Item Env:ACTUALIZAR_ESPERADOS
```
