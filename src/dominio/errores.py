"""Errores del dominio.

Un error de **regla de negocio** viaja con su identificador (RN-xx) para que la API lo devuelva
como 422 y para que las pruebas puedan afirmar *qué* regla falló, no solo que falló.
"""

from __future__ import annotations


class ErrorDominio(ValueError):
    """Dato inválido del dominio (formato, obligatoriedad, coherencia)."""


class ErrorReglaNegocio(ErrorDominio):
    """Regla de negocio incumplida (se expone como 422 en el contrato)."""

    def __init__(self, regla: str, mensaje: str) -> None:
        super().__init__(f"[{regla}] {mensaje}")
        self.regla = regla
        self.mensaje = mensaje
