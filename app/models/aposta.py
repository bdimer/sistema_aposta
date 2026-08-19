"""Modelo ORM que representa uma aposta e preserva sua ODD contratada."""


from typing import TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.enums import SelecaoAposta, StatusAposta

# Este bloco ajuda o editor, mas não executa quando a aplicação está rodando.
if TYPE_CHECKING:
    from app.models.partida import Partida
    from app.models.usuario import Usuario


# Declara a classe persistente correspondente à tabela de apostas.
class Aposta(Base):
    """Registra palpite, valor, multiplicador, ODD e resultado financeiro."""

    __tablename__ = "apostas"
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    partida_id: Mapped[int] = mapped_column(ForeignKey("partidas.id"), index=True)
    gols_casa: Mapped[int] = mapped_column(Integer, nullable=False)
    gols_visitante: Mapped[int] = mapped_column(Integer, nullable=False)
    selecao: Mapped[SelecaoAposta] = mapped_column(
        SqlEnum(SelecaoAposta, native_enum=False), nullable=False
    )
    valor_base: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    multiplicador: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    odd_registrada: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    premio: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    status: Mapped[StatusAposta] = mapped_column(
        SqlEnum(StatusAposta, native_enum=False),
        default=StatusAposta.PENDENTE,
        nullable=False,
    )
    # Registra automaticamente o instante em que a aposta foi criada.
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Continua nulo até a aposta ser vencedora, perdedora ou devolvida.
    liquidado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    usuario: Mapped["Usuario"] = relationship(back_populates="apostas")
    partida: Mapped["Partida"] = relationship(back_populates="apostas")

    # Declara uma propriedade calculada que não cria outra coluna no banco.
    @property
    def valor_total(self) -> Decimal:
        """Calcula o total comprometido depois das multiplicações."""

        # Multiplica o valor original pelo fator acumulado da aposta.
        return self.valor_base * self.multiplicador