"""Define os formatos de entrada e saída relacionados às partidas."""

from datetime import datetime
# Importa Decimal para preservar a precisão das ODDs.
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import StatusPartida


class PartidaBase(BaseModel):
    """Contém as informações básicas de uma partida."""

    time_casa: str = Field(
        min_length=2,
        max_length=120,
    )

    time_visitante: str = Field(
        min_length=2,
        max_length=120,
    )

    inicio_em: datetime
    # Identifica a fase, como grupos, oitavas ou final.
    fase: str = Field(
        min_length=2,
        max_length=60,
    )

    # Restringe o status aos valores definidos pelo sistema.
    status: StatusPartida = StatusPartida.AGENDADA


# Define os dados usados internamente ao importar uma partida.
class PartidaImport(PartidaBase):
    """Representa uma partida recebida da API de futebol."""

    # Mantém o identificador fornecido pela API externa.
    external_id: int = Field(gt=0)

    # O placar pode estar ausente enquanto a partida não terminar.
    gols_casa: int | None = Field(
        default=None,
        ge=0,
    )

    # O placar visitante também começa sem valor.
    gols_visitante: int | None = Field(
        default=None,
        ge=0,
    )


# Define a entrada usada pelo administrador para informar o resultado.
class ResultadoPartidaUpdate(BaseModel):
    """Representa o placar final informado para uma partida."""

    # Impede que o placar da casa seja negativo.
    gols_casa: int = Field(ge=0)
    # Impede que o placar visitante seja negativo.
    gols_visitante: int = Field(ge=0)


# Define a resposta pública de uma partida.
class PartidaResponse(PartidaBase):
    """Representa uma partida devolvida pela API."""

    # Permite que o schema leia diretamente um objeto SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)
    id: int
    # Identificador original recebido da API de futebol.
    external_id: int

    # Placar da casa, caso a partida já tenha terminado.
    gols_casa: int | None
    # Placar visitante, caso a partida já tenha terminado.
    gols_visitante: int | None

    # ODD atual calculada para apostas no time da casa.
    odd_casa: Decimal
    # ODD atual calculada para apostas no time visitante.
    odd_visitante: Decimal


# Define um resumo da sincronização com a API externa.
class SincronizacaoResponse(BaseModel):
    """Informa quantas partidas foram criadas ou atualizadas."""

    # Quantidade de partidas que ainda não existiam no banco.
    partidas_criadas: int

    # Quantidade de partidas existentes que receberam novos dados.
    partidas_atualizadas: int


# Define o resumo devolvido depois de processar um resultado.
class LiquidacaoResponse(BaseModel):
    """Resume os efeitos da liquidação de uma partida."""

    # Identifica a partida processada.
    partida_id: int
    # Mostra o placar final em formato textual.
    placar: str
    # Conta quantas apostas receberam prêmio.
    apostas_vencedoras: int
    # Conta quantas apostas foram definitivamente perdidas.
    apostas_perdedoras: int
    # Conta quantas apostas foram devolvidas.
    apostas_devolvidas: int
    # Conta contas inativadas por falência.
    usuarios_inativados: int
    # Soma todos os prêmios e valores devolvidos.
    total_creditado: Decimal