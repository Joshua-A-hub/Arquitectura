# Especificación de Arquitectura — MVC con visión a Hexagonal

**Origen:** el caso exige *"una arquitectura monolítica limpia utilizando el patrón MVC"* y que el
diseño *"permita una fácil migración a futuro hacia una **Arquitectura Hexagonal o Clean
Architecture**, preparándose para escalar a microservicios cuando la empresa crezca"*, con la
exigencia explícita de que **"este detalle debe verse claramente en los specs"**.

Este documento son los **requisitos de arquitectura (ASR)** verificables. Los diagramas están en
[`docs/arquitectura/`](../../docs/arquitectura/README.md) y las decisiones en
[`specs/adr/`](../adr/).

---

## 1. Requisitos de arquitectura

| ID | Requisito | Nivel | Verificación |
|---|---|---|---|
| **ASR-01** | El sistema MUST organizarse como **monolito** con las tres capas del patrón MVC: Modelo, Vista y Controlador | MUST | `docs/arquitectura/01-mvc-capas.svg` |
| **ASR-02** | Las dependencias MUST apuntar hacia el dominio: Vista → Controlador → Modelo; nunca al revés | MUST | revisión de imports; `grep` de framework dentro de `src/dominio` |
| **ASR-03** | El dominio MUST NOT importar el framework web, el driver de base de datos ni el cliente HTTP de SUNAT | MUST | `grep -r "fastapi\|sqlite3\|requests" src/dominio` vacío |
| **ASR-04** | Toda salida del dominio (persistencia, XML, firma, envío) MUST declararse como **puerto** (interfaz) | MUST | [`src/puertos.py`](../../src/puertos.py): 5 puertos de salida |
| **ASR-05** | La migración a Hexagonal MUST ser posible **sin reescribir reglas de negocio**: solo se agregan adaptadores | MUST | tabla de equivalencia MVC↔Hexagonal en `docs/arquitectura/README.md` |
| **ASR-06** | Un módulo del dominio MUST poder extraerse como microservicio sin cambiar su contrato | SHOULD | el contrato OpenAPI no depende del despliegue |
| **ASR-07** | La aplicación MUST ejecutarse nativamente en **Windows y Android**, empaquetada como **MSI** o **APK** | MUST | [`docs/arquitectura/06-distribucion-msi-apk.md`](../../docs/arquitectura/06-distribucion-msi-apk.md) · [ADR-0003](../adr/0003-estrategia-multiplataforma.md) |
| **ASR-08** | El **contrato** (OpenAPI + DTOs) MUST ser la única frontera entre cliente y servicio | MUST | [`specs/contracts/facturacion-api.yaml`](../contracts/facturacion-api.yaml) |
| **ASR-09** | Las reglas de negocio MUST poder probarse sin servidor, sin base de datos y sin red | SHOULD | `tests/unit/` del mapa de pruebas |
| **ASR-10** | Toda decisión arquitectónica significativa MUST registrarse como ADR | MUST | 3 ADR en [`specs/adr/`](../adr/) |
| **ASR-11** | La validación formal del XML MUST ocurrir en el dominio/aplicación, no en la vista | MUST | RN-18; el certificado nunca llega al cliente |

## 2. Cómo se ve MVC en los specs

| Capa MVC | Especificada en | Responsabilidad | No puede |
|---|---|---|---|
| **Vista** | `specs/contracts/facturacion-api.yaml` (frontera de servicio; la UI es fase 2, `src/vistas/`) | exponer los casos de uso al cliente | calcular impuestos |
| **Controlador** | `specs/features/casos-de-uso.md` (CU-01..CU-10) | orquestar el caso de uso y decidir la respuesta HTTP | acceder a la base de datos directamente |
| **Modelo** | `specs/domain/modelo-dominio.md` + `reglas-negocio.md` | entidades, invariantes, cálculo de tributos, numeración | conocer la pantalla o la tabla |

## 3. Cómo se ve la visión hexagonal en los specs

| Elemento hexagonal | Especificado en | Implementación futura |
|---|---|---|
| **Núcleo (dominio)** | `specs/domain/*` | `src/dominio/` |
| **Puerto de entrada** | `specs/features/casos-de-uso.md` + `src/puertos.py` | `IEmisionService`, `INotaService`, `IMigracionService` |
| **Puerto de salida** | `src/puertos.py` | `IComprobanteRepository`, `IXmlBuilder`, `IFirmaDigital`, `ISunatGateway`, `IValidadorXsd` |
| **Adaptador de entrada** | `facturacion-api.yaml` | controlador REST, CLI, cliente Flutter |
| **Adaptador de salida** | `specs/contracts/ubl/` + `docs/arquitectura/06` | repositorio SQLite, generador UBL, cliente OSE |

## 4. Regla de dependencia (la que hace posible la migración)

```text
 Vista  →  Controlador  →  Dominio  ←  Adaptador
                              ↑
                          Puerto (interfaz)
```

- El dominio declara **qué necesita** (puertos); la infraestructura provee **cómo** (adaptadores).
- Invertir la flecha es lo único que cambia al migrar de MVC a Hexagonal: los controladores dejan de
  instanciar clases concretas y reciben interfaces.
- **No** se reescribe el dominio: se mueve y se le inyectan dependencias.

## 5. Plan de migración (4 pasos, sin big bang)

| Paso | Acción | Criterio de terminado |
|---|---|---|
| 1 | Declarar puertos de salida *(hecho en fase 1)* | `src/puertos.py` con 5 interfaces |
| 2 | Extraer servicios de dominio desde los controladores | controladores sin cálculo de impuestos |
| 3 | Invertir dependencias por constructor | controladores dependen de interfaces |
| 4 | Extraer el módulo de emisión como servicio propio | el contrato no cambia al desplegarlo aparte |

## 6. Atributos de calidad derivados

| Atributo | ASR | Cómo se garantiza | Evidencia |
|---|---|---|---|
| **Modificabilidad** | ASR-03, ASR-05 | dominio aislado; cambiar SQLite no toca reglas | tabla de equivalencia |
| **Testabilidad** | ASR-09 | reglas puras, sin infraestructura | mapa de pruebas en `tests/README.md` |
| **Portabilidad** | ASR-07 | cliente delgado + contrato | ADR-0003 |
| **Trazabilidad** | ASR-08, ASR-10 | contrato + ADR + matriz normativa | 59 cruces |
| **Escalabilidad** | ASR-06 | puertos permiten extraer módulos | plan de migración |

## 7. Requisitos no funcionales (RNF)

Un esqueleto técnico sin números no se puede verificar. Estos son los objetivos medibles; se ajustan
con el negocio en la fase 2.

| ID | Categoría | Requisito | Métrica objetivo | Cómo se verifica |
|---|---|---|---|---|
| **RNF-01** | Rendimiento | Emisión completa (validar + calcular + XML + firmar + XSD) | **P95 < 800 ms** sin contar la respuesta de la OSE | prueba de carga con 20 líneas |
| **RNF-02** | Rendimiento | Cálculo de tributos de una línea | **< 5 ms** | prueba unitaria cronometrada |
| **RNF-03** | Capacidad | Volumen diario / pico | **500 comprobantes/día**, pico **20/min** | simulación de lote |
| **RNF-04** | Disponibilidad | Horario comercial | **99%** (8×5); el modo offline permite emitir y encolar | monitoreo + prueba sin red |
| **RNF-05** | Auditoría | Conservación de XML + CDR + hash | **no menor al plazo de prescripción tributaria** (configurable, por defecto 4 años) | política de retención |
| **RNF-06** | Seguridad | Autenticación y secretos | JWT del emisor; certificado **solo en el servidor**; TLS 1.2+ | revisión del paquete cliente |
| **RNF-07** | Usabilidad | Emitir una factura de 3 líneas | **≤ 2 minutos** por operador entrenado | prueba con usuario real |
| **RNF-08** | Compatibilidad | Plataformas soportadas | **Windows 10+** y **Android 7.0+** | matriz de pruebas |
| **RNF-09** | Mantenibilidad | Cobertura y aislamiento | **≥ 80%** en dominio; **0** imports de framework en el dominio | cobertura + `grep` |
| **RNF-10** | Recuperación | Ante caída del servicio | **RTO 4 h**, **RPO 24 h**; el XML emitido no se pierde | simulacro de restauración |

> Regla de lectura: si un RNF no tiene métrica, no es requisito, es deseo. Por eso cada fila trae un
> número y una forma de comprobarlo.

---

## 8. Fuera de alcance de esta fase

- Implementación de las capas (fase 2).
- Despliegue real en contenedores o nube.
- Observabilidad (métricas, trazas) distribuida.
