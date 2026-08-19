"""Define os formatos de entrada e saída relacionados às apostas."""

from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import (
    SelecaoAposta,
    StatusAposta,
)

# Define os dados necessários para registrar uma aposta.
class ApostaCreate(BaseModel):
    """Representa uma nova aposta enviada pelo usuário."""

    # Identifica a partida escolhida dentro do nosso banco.
    partida_id: int = Field(gt=0)
    # Impede placares negativos para o time da casa.
    gols_casa: int = Field(ge=0)
    # Impede placares negativos para o time visitante.
    gols_visitante: int = Field(ge=0)
    # Exige um valor positivo com no máximo duas casas decimais.
    valor_apostado: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )


# Define os fatores aceitos em uma multiplicação.
class MultiplicacaoAposta(BaseModel):
    """Representa o fator aplicado a uma aposta existente."""

    # Literal recusa automaticamente números fora de 2, 3, 4 e 5.
    multiplicador: Literal[2, 3, 4, 5]


# Define os dados públicos devolvidos após uma operação.
class ApostaResponse(BaseModel):
    """Representa uma aposta sem expor objetos internos do ORM."""

    # Permite que o Pydantic leia diretamente um objeto SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)
    # Identificador interno da aposta.
    id: int
    # Identifica o dono da aposta.
    usuario_id: int
    # Identifica a partida escolhida.
    partida_id: int
    # Guarda o placar previsto para o time da casa.
    gols_casa: int
    # Guarda o placar previsto para o time visitante.
    gols_visitante: int
    # Informa se o palpite representa casa, visitante ou empate.
    selecao: SelecaoAposta
    # Guarda o valor original da aposta.
    valor_base: Decimal
    # Guarda o fator acumulado após multiplicações.
    multiplicador: int
    # Mostra o valor total comprometido pelo usuário.
    valor_total: Decimal
    # Preserva a ODD aceita quando a aposta foi criada.
    odd_registrada: Decimal
    # Guarda o prêmio pago depois da liquidação.
    premio: Decimal
    # Informa se a aposta está pendente, ganhou, perdeu ou foi devolvida.
    status: StatusAposta
    # Informa quando a aposta foi registrada.
    criado_em: datetime
    # Continua vazio enquanto a aposta ainda não foi processada.
    liquidado_em: datetime | None