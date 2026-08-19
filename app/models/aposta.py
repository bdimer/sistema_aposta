"""Modelo ORM que representa uma aposta e preserva sua ODD contratada."""

# Importa TYPE_CHECKING para declarar relações sem causar importação circular.
from typing import TYPE_CHECKING
# Importa datetime para registrar criação e liquidação.
from datetime import datetime
# Importa Decimal para valores financeiros/pontos e ODDs precisas.
from decimal import Decimal
# Importa tipos, chaves estrangeiras e função de data do SQLAlchemy.
from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, func
# Importa tipos modernos do ORM para colunas e relacionamentos.
from sqlalchemy.orm import Mapped, mapped_column, relationship
# Importa a base e os enums que limitam seleção e estado da aposta.
from app.database import Base
from app.models.enums import SelecaoAposta, StatusAposta

# Este bloco ajuda o editor, mas não executa quando a aplicação está rodando.
if TYPE_CHECKING:
    # Importa o tipo Partida somente para completar a anotação abaixo.
    from app.models.partida import Partida
    # Importa o tipo Usuario somente para completar a anotação abaixo.
    from app.models.usuario import Usuario


# Declara a classe persistente correspondente à tabela de apostas.
class Aposta(Base):
    """Registra palpite, valor, multiplicador, ODD e resultado financeiro."""

    # Define o nome físico da tabela SQL.
    __tablename__ = "apostas"
    # Cria o identificador único da aposta.
    id: Mapped[int] = mapped_column(primary_key=True)
    # Liga a aposta ao usuário que a realizou.
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    # Liga a aposta à partida correspondente.
    partida_id: Mapped[int] = mapped_column(ForeignKey("partidas.id"), index=True)
    # Guarda o placar previsto para o time da casa.
    gols_casa: Mapped[int] = mapped_column(Integer, nullable=False)
    # Guarda o placar previsto para o time visitante.
    gols_visitante: Mapped[int] = mapped_column(Integer, nullable=False)
    # Registra o lado derivado do placar para determinar a ODD aplicável.
    selecao: Mapped[SelecaoAposta] = mapped_column(
        SqlEnum(SelecaoAposta, native_enum=False), nullable=False
    )
    # Armazena o valor original informado antes de multiplicações posteriores.
    valor_base: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    # Guarda o fator acumulado, começando em uma vez o valor original.
    multiplicador: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # Preserva a ODD aceita no registro para não mudar prêmios retroativamente.
    odd_registrada: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    # Começa zerado e receberá o valor pago após a liquidação.
    premio: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    # Mantém a aposta pendente até o processamento do resultado da partida.
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
    # Permite navegar da aposta até o objeto completo do usuário.
    usuario: Mapped["Usuario"] = relationship(back_populates="apostas")
    # Permite navegar da aposta até o objeto completo da partida.
    partida: Mapped["Partida"] = relationship(back_populates="apostas")

    # Declara uma propriedade calculada que não cria outra coluna no banco.
    @property
    def valor_total(self) -> Decimal:
        """Calcula o total comprometido depois das multiplicações."""

        # Multiplica o valor original pelo fator acumulado da aposta.
        return self.valor_base * self.multiplicador