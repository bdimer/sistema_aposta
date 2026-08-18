"""Expõe os modelos e garante que todos sejam registrados no SQLAlchemy."""

# Importa Aposta para registrar a tabela apostas na metadata compartilhada.
from app.models.aposta import Aposta
# Importa os enums para facilitar seu uso por outros módulos.
from app.models.enums import SelecaoAposta, StatusAposta, StatusPartida
# Importa Partida para registrar a tabela partidas na metadata compartilhada.
from app.models.partida import Partida
# Importa Usuario para registrar a tabela usuarios na metadata compartilhada.
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
