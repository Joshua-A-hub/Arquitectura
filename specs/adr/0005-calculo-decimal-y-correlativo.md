# ADR-0005: Cálculo tributario con `Decimal`, redondeo y correlativo atómico

- **Estado:** Aceptada
- **Fecha:** 2026-11-05
- **Decisores:** Alvarado Ichpas Benny Joshua (arquitectura), área tributaria

## Contexto

Un comprobante tributario no admite errores de un céntimo: SUNAT reconcilia
`valor unitario × cantidad`, `base × tasa = impuesto` y la suma de líneas con los totales. El
proyecto arrastraba dos riesgos:

1. Importes en coma flotante: `0.1 + 0.2 != 0.3` y los redondeos derivan.
2. Un error real detectado por las pruebas: el IGV se calculaba sobre la base **ya redondeada**, lo
   que desviaba un céntimo (1.52 en lugar de 1.53 en la línea de la bolsa).
3. El correlativo debe ser único por `tipo + serie` y no puede tener huecos.

## Alternativas consideradas

| Opción | Veredicto |
|---|---|
| `float` con `round()` | **Descartada**: precisión binaria y redondeo bancario |
| `Decimal` y redondeo al final de cada línea | **Elegida** |
| Redondear en cada paso intermedio | Descartada: es la causa del desvío de un céntimo |

## Decisión

1. **Todo importe y cantidad es `Decimal`.** Los DTO los reciben como *string* decimal
   (`"1250.50"`), nunca como número.
2. **Redondeo half-up a 2 decimales** (`ROUND_HALF_UP`), y **una sola vez por importe**:
   - el impuesto se calcula sobre la base **exacta** y se redondea el resultado;
   - `valor_venta` de la línea es la base exacta redondeada;
   - los totales son la **suma de líneas ya redondeadas**, nunca el recálculo desde los unitarios.
3. **El valor unitario conserva 6 decimales** en el XML (`cac:Price/cbc:PriceAmount`): con 2, el
   producto por la cantidad no reconcilia con `LineExtensionAmount`.
4. **Correlativo**: entero positivo por `tipo + serie`, formato de 8 dígitos
   (`F001-00000123`); se asigna **dentro de la transacción** del repositorio y se libera si la
   emisión falla (RN-11); `(tipo, serie, correlativo)` es único (RN-12).

## Consecuencias

**Positivas**

- El cuadre `base × tasa = impuesto` se cumple y se prueba en los tres sistemas del ISC.
- El XML es reproducible byte a byte (determinismo) gracias a `Decimal` y `xsdata`.

**Negativas**

- `float` queda prohibido en la frontera: el mapeo de JSON a dominio debe convertir a `Decimal`
  (lo hace la CLI y debe hacerlo la API).

## Verificación

| Verificación | Criterio |
|---|---|
| Redondeo | `test_rn08_redondeo.py`: half-up y cálculo sobre la base exacta |
| Cuadre | `test_rn06_isc_catalogo_08.py`: `base × Percent / 100 = TaxAmount` |
| Valor unitario | `test_rn04_valor_unitario.py`: `precio × cantidad ≈ LineExtensionAmount` |
| Correlativo | `test_rn11_correlativo.py`: formato y rango |
