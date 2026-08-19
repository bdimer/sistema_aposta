"""Define valores fechados para estados importantes do domínio."""

from enum import Enum


# Representa os estados relevantes recebidos da API de futebol.
class StatusPartida(str, Enum):
    """Estados possíveis de uma partida."""

    # Indica que a partida ainda pode receber apostas.
    AGENDADA = "SCHEDULED"
    # Indica que a partida está acontecendo e não aceita novas apostas.
    EM_ANDAMENTO = "IN_PLAY"
    # Indica que a partida terminou e pode ser liquidada.
    ENCERRADA = "FINISHED"
    # Preserva partidas adiadas informadas pelo provedor externo.
    ADIADA = "POSTPONED"
    # Preserva partidas canceladas informadas pelo provedor externo.
    CANCELADA = "CANCELLED"


# Registra qual lado o placar escolhido pelo usuário aponta como vencedor.
class SelecaoAposta(str, Enum):
    """Lado escolhido implicitamente pelo placar informado na aposta."""

    # O palpite prevê vitória do time da casa.
    CASA = "HOME"
    # O palpite prevê vitória do time visitante.
    VISITANTE = "AWAY"
    # O palpite prevê empate; será devolvido se o resultado real também empatar.
    EMPATE = "DRAW"


# Controla se uma aposta ainda aguarda resultado ou já foi processada.
class StatusAposta(str, Enum):
    """Estados do ciclo de vida de uma aposta."""

    # A aposta foi registrada e aguarda o encerramento da partida.
    PENDENTE = "PENDING"
    # O usuário acertou e recebeu o prêmio calculado.
    VENCEDORA = "WON"
    # O usuário errou e o débito feito na criação tornou-se definitivo.
    PERDEDORA = "LOST"
    # O valor foi devolvido em razão de empate ou cancelamento aplicável.
    DEVOLVIDA = "REFUNDED"
