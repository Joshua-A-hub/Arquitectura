"""Genera un certificado autofirmado SOLO para probar la firma XMLDSig.

No usar en producción: el certificado real lo emite una entidad certificadora autorizada y se
guarda como secreto del servidor (nunca en el repositorio).

    python scripts/generar_certificado_prueba.py --salida out/certificado-prueba
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def generar(destino: Path, titular: str) -> tuple[Path, Path]:
    destino.mkdir(parents=True, exist_ok=True)
    clave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nombre = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, titular)])
    ahora = dt.datetime.now(dt.UTC)
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nombre)
        .issuer_name(nombre)
        .public_key(clave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(ahora)
        .not_valid_after(ahora + dt.timedelta(days=3650))
        .sign(clave, hashes.SHA256())
    )
    ruta_clave = destino / "clave-prueba.pem"
    ruta_certificado = destino / "certificado-prueba.pem"
    ruta_clave.write_bytes(
        clave.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    ruta_certificado.write_bytes(certificado.public_bytes(serialization.Encoding.PEM))
    return ruta_clave, ruta_certificado


def main() -> int:
    parser = argparse.ArgumentParser(description="Certificado autofirmado para pruebas")
    parser.add_argument("--salida", type=Path, default=Path("out/certificado-prueba"))
    parser.add_argument("--titular", default="ABC SOFTWARE CORP SAC - PRUEBA")
    args = parser.parse_args()
    clave, certificado = generar(args.salida, args.titular)
    print(f"clave:      {clave}")
    print(f"certificado:{certificado}")
    print("Aviso: certificado de PRUEBA, no sirve para SUNAT.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
