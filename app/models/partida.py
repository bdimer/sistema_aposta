"""Modelo ORM que representa partidas importadas da API de futebol."""

# Importa TYPE_CHECKING para declarar relações sem causar importação circular.
from typing import TYPE_CHECKING
# Importa datetime para armazenar o instante completo da partida.
from datetime import datetime
# Importa Decimal para guardar ODDs com precisão decimal.
from decimal import Decimal
# Importa os tipos SQL necessários às colunas da partida.
from sqlalchemy import DateTime, Enum as SqlEnum, Integer, Numeric, String
# Importa tipos modernos do ORM para colunas e relacionamentos.
from sqlalchemy.orm import Mapped, mapped_column, relationship
# Importa a base das tabelas e o enum permitido para status.
from app.database import Base
from app.models.enums import StatusPartida

# O conteúdo deste bloco é utilizado somente por editores e verificadores.
if TYPE_CHECKING:
    # Esclarece que o relacionamento contém objetos do modelo Aposta.
    from app.models.aposta import Aposta


# Declara a representação Python da tabela de partidas.
class Partida(Base):
    """Persiste agenda, placar, estado e ODDs atuais de uma partida."""

    # Define o nome físico da tabela no banco de dados.
    __tablename__ = "partidas"
    # Cria uma chave primária interna independente do provedor externo.
    id: Mapped[int] = mapped_column(primary_key=True)
    # Guarda o ID da Football Data e evita importar o mesmo jogo duas vezes.
    external_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    # Armazena o nome do time que joga em casa.
    time_casa: Mapped[str] = mapped_column(String(120), nullable=False)
    # Armazena o nome do time visitante.
    time_visitante: Mapped[str] = mapped_column(String(120), nullable=False)
    # Guarda data, hora e fuso em uma única informação ordenável.
    inicio_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # Registra a fase da competição, como grupos ou oitavas de final.
    fase: Mapped[str] = mapped_column(String(60), nullable=False)
    # Restringe o status aos valores definidos pelo enum do domínio.
    status: Mapped[StatusPartida] = mapped_column(
        SqlEnum(StatusPartida, native_enum=False),
        default=StatusPartida.AGENDADA,
        nullable=False,
    )
    # Permite valor nulo enquanto a partida ainda não possui resultado.
    gols_casa: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Permite valor nulo enquanto a partida ainda não possui resultado.
    gols_visitante: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Começa em 2.0 e será recalculada quando apostas forem registradas.
    odd_casa: Mapped[Decimal] = mapped_column(
        Numeric(10, 4), default=Decimal("2.0"), nullable=False
    )
    # Começa em 2.0 e será recalculada quando apostas forem registradas.
    odd_visitante: Mapped[Decimal] = mapped_column(
        Numeric(10, 4), default=Decimal("2.0"), nullable=False
    )
    # Relaciona a partida a todas as apostas feitas nela.
    apostas: Mapped[list["Aposta"]] = relationship(back_populates="partida")
