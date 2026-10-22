# Distribución multiplataforma — Windows y Android

**Requisito del caso:** *"Debe correr de forma nativa en Windows y en Android, y empaquetarse
obligatoriamente en un formato de instalación amigable (instalador MSI para escritorio o APK para
Android)."*

---

## 1. Decisión arquitectónica

El sistema se compone de **dos piezas** que se empaquetan juntas en cada plataforma:

```text
┌─────────────────────────────────────────────┐
│  Aplicación cliente (UI)                    │
│  · Windows  → instalador MSI                │
│  · Android  → APK                           │
└───────────────────┬─────────────────────────┘
                    │ HTTP (contrato OpenAPI)
┌───────────────────▼─────────────────────────┐
│  Servicio de facturación (monolito MVC)     │
│  · Local en el equipo (Windows)             │
│  · Local en el dispositivo (Android)        │
└───────────────────┬─────────────────────────┘
                    │
        SQLite local + XML firmados
```

**Por qué no una sola app empaquetada con toda la lógica:** el dominio debe poder moverse a un
servidor (microservicio) sin reescribir la UI. Separar cliente y servicio **es** la preparación para
la migración a hexagonal.

## 2. Opciones evaluadas

| Opción | Windows (MSI) | Android (APK) | Esfuerzo | Riesgo |
|---|---|---|---|---|
| **A. Cliente Flutter + servicio Python** | Sí (instalador propio / Inno Setup) | Sí (APK nativo) | Medio | dos lenguajes; UI aislada por el contrato |
| **B. .NET MAUI + backend .NET** | Sí (MSI/MSIX natural) | Sí (APK) | Alto | cambia el stack del equipo |
| **C. Cliente web + WebView** | Sí (MSI con WebView2) | Sí (APK con WebView) | Bajo | dependencia del motor del sistema |
| **D. Kivy / BeeWare (todo Python)** | Sí (exe + MSI) | Sí (APK con Buildozer) | Medio | empaquetado Android frágil |

**Decisión: opción A** — cliente Flutter + servicio Python, registrada en
[`ADR-0003`](../../specs/adr/0003-estrategia-multiplataforma.md). El **contrato API no cambia**: eso
es exactamente lo que compra la arquitectura hexagonal.

## 3. Empaquetado

### Windows — MSI

| Aspecto | Definición |
|---|---|
| Herramienta | **WiX Toolset** — genera MSI real (Inno Setup queda descartado: produce EXE) |
| Contenido | ejecutable + recursos + servicio local |
| Requisitos | Windows 10 1809 o superior |
| Instalación | por usuario, sin privilegios de administrador |
| Datos | `%LOCALAPPDATA%\ABCFacturacion\` (SQLite + XML) |
| Desinstalación | conserva los XML emitidos (evidencia tributaria) |

### Android — APK

| Aspecto | Definición |
|---|---|
| Formato | APK firmado (release) |
| Android mínimo | API 24 (Android 7.0) |
| Permisos | almacenamiento (XML/PDF) e internet (envío a OSE) |
| Almacenamiento | base local del dispositivo; sincronización opcional |
| Distribución | APK directo (el caso no exige Play Store) |

## 4. Consecuencias en el diseño

| Consecuencia | Detalle |
|---|---|
| **El dominio no depende de la UI** | La misma lógica corre en escritorio y móvil |
| **El XML se firma donde está el certificado** | El certificado del emisor vive en el servicio, no en el cliente |
| **Modo sin conexión** | El servicio local emite y deja el comprobante `PENDIENTE_ENVIO` hasta recuperar red |
| **Tamaño del instalador** | Se comprime el runtime; los XML se generan en tiempo de ejecución |
| **Actualizaciones** | MSI: actualización en sitio; APK: reinstalación con misma firma |

## 5. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| Certificado digital en un dispositivo móvil es riesgoso | en Android, la emisión se delega al servicio; el certificado nunca sale del servidor |
| Diferencias de sistema de archivos | capa de almacenamiento abstracta (puerto de salida) |
| Consumo de batería/datos | envío diferido en lote cuando hay Wi-Fi |
| Fragmentación de versiones Android | API 24+ y pruebas en 3 densidades |

## 6. Criterios de aceptación

| ID | Criterio |
|---|---|
| DIS-01 | El MSI instala y desinstala sin dejar residuos (salvo XML emitidos) |
| DIS-02 | El APK instala en Android 7+ y abre sin conexión |
| DIS-03 | La misma petición al contrato produce el mismo comprobante en ambas plataformas |
| DIS-04 | Sin red, el comprobante queda `PENDIENTE_ENVIO` y no se pierde |
| DIS-05 | El certificado digital nunca se almacena en el cliente |
