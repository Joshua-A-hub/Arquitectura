# Regenera las clases Python tipadas desde los XSD oficiales de OASIS UBL 2.1.
#
# Fuente: specs/contracts/ubl/oficial/  (Invoice, CreditNote, DebitNote + 13 common)
# Salida: src/adapters/outbound/ubl/generated/
#
# Las clases generadas NO se editan a mano: si hay que cambiar algo, se cambia el XSD
# o se corrige el adaptador. Para verificar que están al día:
#
#   .\scripts\generar_clases_ubl.ps1
#   git diff --stat src/adapters/outbound/ubl/generated    # sin cambios = al día
#
# Requisitos:  pip install -r requirements-dev.txt   (xsdata[cli] + ruff)

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

python -m xsdata generate specs/contracts/ubl/oficial/maindoc --package src.adapters.outbound.ubl.generated

if ($LASTEXITCODE -ne 0) {
    Write-Error "xsdata falló: revisa que 'ruff' esté en el PATH (lo instala xsdata[cli])."
    exit $LASTEXITCODE
}

Write-Host "Clases regeneradas en src/adapters/outbound/ubl/generated/"
