# Caso de examen — Transcripción y requisitos

**Fuente:** `caso/20261022_092222.jpg.jpeg` (foto del examen)
**Universidad Nacional Agraria de la Selva** — Facultad de Ingeniería en Informática y Sistemas
**Curso:** Arquitectura de Software — Examen de Medio Curso, Grupo "A"
**Fecha:** 19 de octubre de 2026 — **Duración:** 2:00 horas

---

## 1. Descripción del caso (transcripción)

Ha sido contratado por **ABC Software Corp**, una empresa mediana que comercializa abarrotes y
mercadería al por mayor y menor. Tienen un software operativo básico que cumple con lo justo y
necesario para registrar el día a día del almacén (controlan fichas sencillas con campos como
fecha, ingreso, salida, producto y un número de documento interno bastante informal).

El problema grave es que la **SUNAT**, mediante la **RS N° 097-2012**, la **RS N° 234-2006** y las
normativas modernas de masificación de comprobantes electrónicos, les exige llevar registros
formales y emitir comprobantes legales estructurados bajo el estándar **UBL** (Universal Business
Language), cuyo estándar puede estudiarse en la web de **OASIS**. El sistema actual no valida RUCs,
no calcula correctamente los impuestos (**IGV, ISC, ICBPER**, etc.), no genera XMLs firmados
digitalmente y menos se comunica con un **Operador de Servicios Electrónicos (OSE)** o directamente
con la SUNAT.

> **Misión:** como líder de equipo de desarrollo **no es ponerte a codificar**, sino mediante la
> metodología **Spec-First**: primero definir las reglas, contratos de datos, validaciones y
> contratos de interfaz **antes de escribir una sola línea de lógica de negocio**, estudiando el
> archivo `UBL-Invoice-2.1.xsd`, pero deberás estudiar todas las reglas antes, apoyándote de IA.

## 2. Alcance técnico y restricciones arquitectónicas (transcripción)

- **Legado y migración de datos:** toda la información histórica del software básico (fecha,
  ingreso, salida, producto, `nro_documento`) debe acoplarse y mapearse limpiamente hacia las nuevas
  entidades del sistema **sin perder trazabilidad**.
- **Normativa tributaria peruana:** estricto cumplimiento de los requisitos de SUNAT (catálogos de
  tipos de documentos, afectación al IGV, códigos de moneda, series, correlativos y validaciones de
  emisión). **Punto clave: el catálogo 8 de SUNAT.**
- **Arquitectura base y futura:** inicialmente monolítica limpia usando **MVC**, pero el diseño debe
  desacoplarse para permitir una fácil migración futura hacia **Hexagonal** o **Clean Architecture**,
  preparándose para escalar a microservicios cuando la empresa crezca. *"Este detalle debe verse
  claramente en los specs."*
- **Distribución y multiplataforma:** debe correr de forma **nativa en Windows y en Android**, y
  empaquetarse obligatoriamente en un formato de instalación amigable (**instalador MSI** para
  escritorio o **APK** para Android).

## 3. Descubrimiento de casos de uso (transcripción)

La gerencia desea que se detallen los casos posibles, revisando opiniones de usuarios de facturación
electrónica, pudiendo revisar otros softwares en línea como el caso de **Nubefact** (usuario DEMO).

## 4. Entregable esperado (transcripción)

Como entregable de la primera fase (**Spec-First**), un **esqueleto de especificaciones técnicas**
que debe contener:

1. **Modelo de Dominio y Contratos** (DTOs / Schemas).
2. **Diagramas de Arquitectura MVC** con visión a **Hexagonal**.
3. **Especificación de Endpoints / Servicios** (Contratos API).
4. **Matriz de Trazabilidad Normativa** con cruces entre datos SUNAT y datos UBL.

---

## 5. Requisitos numerados (derivados del caso)

| ID | Requisito | Tipo | Entregable |
|---|---|---|---|
| **REQ-01** | Migrar las fichas históricas (fecha, ingreso, salida, producto, `nro_documento`) a las nuevas entidades sin perder trazabilidad | Funcional / datos | E1 · `docs/arquitectura/05-migracion-legado.md` |
| **REQ-02** | Cumplir la normativa SUNAT vigente (RS 097-2012, RS 234-2006 y masificación CPE) | Normativo | E4 |
| **REQ-03** | Validar RUC y demás documentos de identidad según el **catálogo 8** | Normativo | E1, E4 |
| **REQ-04** | Calcular **IGV, ISC e ICBPER** con precisión y redondeo definido | Funcional | E1, E4 |
| **REQ-05** | Emitir comprobantes electrónicos bajo el estándar **UBL 2.1 Invoice** | Normativo | E1, E3, E4 |
| **REQ-06** | Generar el **XML firmado digitalmente** | Normativo / seguridad | E4 |
| **REQ-07** | Comunicarse con una **OSE** o directamente con SUNAT, y procesar el **CDR** | Integración | E3 · ADR-0002 |
| **REQ-08** | Arquitectura **monolítica limpia con MVC** | Arquitectura | E2 · `specs/architecture/mvc-hexagonal.md` |
| **REQ-09** | Diseño **desacoplado** para migrar a **Hexagonal / Clean** y luego a microservicios | Arquitectura | E2 · `specs/architecture/mvc-hexagonal.md` |
| **REQ-10** | Ejecutarse de forma **nativa en Windows y Android** | Plataforma | `docs/arquitectura/06-distribucion-msi-apk.md` · ADR-0003 |
| **REQ-11** | Empaquetado en **MSI** (escritorio) o **APK** (Android) | Distribución | `docs/arquitectura/06-distribucion-msi-apk.md` · ADR-0003 |
| **REQ-12** | Detallar **casos de uso** del dominio de facturación electrónica | Funcional | E1, features |

## 6. Fuera de alcance de esta fase (declarado)

El enunciado pide **no codificar sin especificar primero**, no "no codificar": la lógica de negocio se
escribe **después** de aprobar los contratos. Por eso esta entrega se detiene al final de la fase 1.

- **Diseño de interfaz de usuario** (pantallas, wireframes, prototipos): **no se diseña**. El
  entregable son especificaciones técnicas; el contrato API es un contrato **de servicio**, no una
  pantalla. La restricción de despliegue (MSI/APK) se documenta como restricción arquitectónica.
- Implementación de la lógica de negocio (fase 2, con los contratos ya cerrados).
- Certificación real como emisor electrónico ante SUNAT y obtención de certificado digital.
- Integración real con una OSE (solo se especifica el contrato y el flujo).
- Contabilidad general, planillas, tesorería.

## 7. Criterio de éxito de la entrega

| Verificación | Cómo se demuestra |
|---|---|
| Los 4 entregables existen | documentos E1–E4 en el repositorio |
| La normativa está cubierta | matriz con ≥ 30 cruces SUNAT ↔ UBL |
| La arquitectura está justificada | 2 diagramas + ADR + plan de migración MVC→Hexagonal |
| Los contratos son coherentes | OpenAPI + JSON Schemas validados por script |
| El legado no se pierde | tabla de mapeo ficha → entidad con trazabilidad |
