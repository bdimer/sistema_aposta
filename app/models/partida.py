
"""Modelo ORM que representa partidas importadas da API de futebol."""


from typing import TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Enum as SqlEnum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.enums import StatusPartida

# O conteúdo deste bloco é utilizado somente por editores e verificadores.
if TYPE_CHECKING:
    from app.models.aposta import Aposta


# Declara a representação Python da tabela de partidas.
class Partida(Base):
    """Persiste agenda, placar, estado e ODDs atuais de uma partida."""

    __tablename__ = "partidas"
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    time_casa: Mapped[str] = mapped_column(String(120), nullable=False)
    time_visitante: Mapped[str] = mapped_column(String(120), nullable=False)
    inicio_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    fase: Mapped[str] = mapped_column(String(60), nullable=False)
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
