# ADR-0003: Estrategia multiplataforma (Windows + Android, MSI + APK)

- **Estado:** Aceptada
- **Fecha:** 22 de octubre de 2026
- **Decisores:** Líder de arquitectura, jefe de sistemas
- **Consultados:** área contable (usuarios finales)

## Contexto

El caso exige que el sistema corra **de forma nativa en Windows y Android**, y que se empaquete
obligatoriamente en **MSI** (escritorio) o **APK** (Android). El equipo actual trabaja en Python y el
proyecto de referencia del curso usa ese stack.

El dominio ya está aislado tras el contrato OpenAPI y los puertos (`src/puertos.py`), así que la
decisión afecta a la **capa de presentación y al empaquetado**, no a las reglas de negocio.

## Opciones consideradas

| Opción | Windows (MSI) | Android (APK) | Lenguajes | Riesgo |
|---|---|---|---|---|
| **A. Cliente Flutter + servicio Python** | instalador propio / Inno Setup | APK nativo | Python + Dart | dos lenguajes, pero la UI queda aislada |
| **B. .NET MAUI + backend .NET** | MSI/MSIX natural | APK | C# | cambia el stack del equipo y del curso |
| **C. Cliente web en WebView + servicio Python** | MSI con WebView2 | APK con WebView | Python + JS | depende del motor del sistema; peor experiencia offline |
| **D. Kivy / BeeWare (todo Python)** | exe + MSI | APK con Buildozer | Python | un solo lenguaje; empaquetado Android frágil |

## Decisión

**Opción A: cliente Flutter + servicio Python (FastAPI, monolito MVC).**

- El **servicio** contiene todo el dominio (reglas, cálculo de tributos, generación del XML, firma) y
  corre en el equipo o en el servidor; expone el contrato de `specs/contracts/`.
- El **cliente Flutter** consume ese contrato y se empaqueta como **MSI** (Windows) y **APK**
  (Android).
- El **certificado digital nunca viaja al cliente**: la firma ocurre en el servicio (ADR-0002).

## Por qué no las otras

- **B (.NET MAUI):** obligaría a reescribir en C# lo que el equipo ya domina en Python, y el proyecto
  de referencia del curso es Python. Costo alto, beneficio bajo.
- **C (WebView):** es la más barata, pero depende del motor del sistema y la experiencia offline es
  pobre justo en el escenario crítico (almacén sin buena red).
- **D (Kivy):** un solo lenguaje, pero el empaquetado Android es el eslabón más frágil y la UI nativa
  queda por debajo de lo que un usuario de facturación espera.

## Consecuencias

**Positivas**
- El dominio se escribe **una vez** y sirve a escritorio, móvil y futuros microservicios.
- El APK y el MSI se generan sin tocar las reglas tributarias.
- El contrato aísla la UI: cambiar de Flutter a otra tecnología no toca el núcleo.

**Negativas / trade-offs**
- Dos lenguajes en el equipo (Python + Dart): se mitiga con el contrato como frontera y con que el
  cliente sea delgado (sin lógica de negocio).
- El MSI requiere un paso de empaquetado adicional (PyInstaller + **WiX Toolset** (MSI)).
- El modo sin conexión obliga a que el servicio local esté disponible en el dispositivo: en Android se
  resuelve con un servicio embebido; es el punto de mayor complejidad técnica.

## Verificación

| Criterio | Cómo se comprueba |
|---|---|
| DIS-01 | el MSI instala y desinstala sin residuos (salvo XML emitidos) |
| DIS-02 | el APK instala en Android 7+ y abre sin conexión |
| DIS-03 | la misma petición produce el mismo comprobante en ambas plataformas |
| DIS-04 | sin red, el comprobante queda `PENDIENTE_ENVIO` y no se pierde |
| DIS-05 | el certificado no aparece en el cliente (búsqueda en el paquete) |

## Estado de la decisión en la entrega

Esta fase **no implementa** el cliente ni el empaquetado, y **no diseña la interfaz de usuario**: la
decisión se registra como restricción de despliegue. El desarrollo de la UI (pantallas, navegación,
prototipos) queda expresamente fuera del alcance del entregable Spec-First; las consecuencias
documentadas están en
[`docs/arquitectura/06-distribucion-msi-apk.md`](../../docs/arquitectura/06-distribucion-msi-apk.md).
