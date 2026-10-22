# Código fuente

**Fase 1 (esta entrega):** solo **puertos** (interfaces). Cero lógica de negocio, porque el enunciado
exige definir reglas, contratos y validaciones **antes** de escribir la primera línea de negocio.

## Qué hay hoy

| Archivo | Contenido |
|---|---|
| `puertos.py` | 3 puertos de entrada (`IEmisionService`, `INotaService`, `IMigracionService`) y 5 de salida (`IComprobanteRepository`, `IXmlBuilder`, `IFirmaDigital`, `ISunatGateway`, `IValidadorXsd`) |

Los puertos salen del contrato (`specs/contracts/facturacion-api.yaml`) y del modelo
(`specs/domain/modelo-dominio.md`), no al revés.

## Qué se implementa en la fase 2 (estructura MVC)

```text
src/
├── puertos.py                  ← interfaces (ya existe)
├── controladores/              ← CAPA CONTROLADOR (MVC)
│   ├── emision_controller.py
│   ├── nota_controller.py
│   └── migracion_controller.py
├── dominio/                    ← CAPA MODELO (MVC) = núcleo hexagonal
│   ├── comprobante.py          entidades y agregados
│   ├── calculadora_tributos.py IGV, ISC, ICBPER (RN-04..RN-09)
│   ├── numeracion.py           series y correlativos (RN-10..RN-12)
│   └── reglas.py               RN-01..RN-24
├── adaptadores/                ← INFRAESTRUCTURA (reemplazable)
│   ├── sqlite_comprobante_repository.py
│   ├── ubl_builder.py
│   ├── firma_xml.py
│   ├── validador_xsd.py
│   └── ose_gateway.py
└── vistas/                     ← CAPA VISTA (MVC)
    ├── api_rest.py             (FastAPI)
    └── cli.py                  (herramientas locales del operador)
```

El cliente de escritorio y móvil es **Flutter** y consume el mismo contrato (ver
[`ADR-0003`](../specs/adr/0003-estrategia-multiplataforma.md)): la UI no contiene reglas de negocio.

## Regla de dependencia (la que hace posible la migración)

```text
vistas → controladores → dominio ← adaptadores
                          ↑
                    puertos.py
```

- `dominio/` **no importa** `fastapi`, `sqlite3` ni `requests`.
- Los adaptadores implementan los puertos; el dominio los recibe inyectados.
- Verificación: `grep -r "fastapi\|sqlite3" src/dominio` debe devolver vacío.

## Orden de implementación sugerido

1. `dominio/calculadora_tributos.py` + pruebas de IGV/ISC/ICBPER (las reglas más delicadas).
2. `dominio/numeracion.py` + `adaptadores/sqlite_comprobante_repository.py`.
3. `adaptadores/ubl_builder.py` + validación contra el perfil UBL.
4. `controladores/` + `vistas/api_rest.py`.
5. `adaptadores/ose_gateway.py` y manejo de CDR.
