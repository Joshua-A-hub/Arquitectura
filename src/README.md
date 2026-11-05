# Código fuente

El proyecto pasó de **solo especificaciones** (primer parcial) a **implementación acotada** (segundo
parcial): el Taller 2 exige generar el XML desde el XSD oficial, y eso necesita dominio y adaptador.

## Estructura

```text
src/
├── domain/                    dominio puro: no conoce HTTP, ni XML, ni la base de datos
│   ├── catalogos.py           catálogos SUNAT 01,02,03,05,06,07,08,09,10,51
│   ├── valores.py             RUC (módulo 11), Serie, Correlativo, DocumentoIdentidad, redondeo
│   ├── tributos.py            IGV 18 %, ISC (3 sistemas del catálogo 08), ICBPER, totales
│   ├── letras.py              importe en letras (leyenda 1000)
│   ├── comprobante.py         agregado Comprobante + Emisor, Cliente, Linea, FormaPago
│   └── errores.py             ErrorDominio / ErrorReglaNegocio (con el RN que falla)
├── adapters/outbound/ubl/
│   ├── generated/             clases producidas por xsdata desde el XSD oficial (NO se editan)
│   ├── generador.py           GeneradorUblXsdata: dominio → clases → XML (puerto IXmlBuilder)
│   ├── validador.py           ValidadorXsd: XML contra el esquema oficial (puerto IValidadorXsd)
│   └── firma/xmldsig.py       FirmadorXmlDsig: XMLDSig dentro de ext:UBLExtensions (puerto IFirmaDigital)
├── cli.py                     adaptadores de entrada (generar-xml y firmar), sin HTTP
└── puertos.py                 interfaz del hexágono
```

## Regla de dependencia

`domain` no importa nada de `adapters` ni de `cli`: los adaptadores dependen del dominio, nunca al
revés. El generador implementa el puerto `IXmlBuilder` de `puertos.py`, así que el caso de uso no sabe
que existe `xsdata`.

## Cómo generar el XML

```powershell
python -m src.cli generar-xml specs/ejemplos/emision-cli.json --salida out
```

El XML se genera **sin firma**: el orden del flujo es generar → validar contra el esquema oficial →
firmar → enviar (RN-18). El adaptador de firma es fase 2.

## Cómo regenerar las clases del XSD

```powershell
pip install -r requirements-dev.txt
.\scripts\generar_clases_ubl.ps1
```

Las clases se versionan: si `git diff` las muestra cambiadas sin que se haya tocado el XSD, algo raro
pasó. La fuente es siempre `specs/contracts/ubl/oficial/`.
