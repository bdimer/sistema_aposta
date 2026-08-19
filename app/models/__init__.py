"""Expõe os modelos e garante que todos sejam registrados no SQLAlchemy."""

from app.models.aposta import Aposta
from app.models.enums import SelecaoAposta, StatusAposta, StatusPartida
from app.models.partida import Partida
from app.models.usuario import Usuario

# Define explicitamente quais nomes públicos este pacote oferece.
__all__ = [
    "Aposta",
    "Partida",
    "SelecaoAposta",
    "StatusAposta",
    "StatusPartida",
    "Usuario",
]
