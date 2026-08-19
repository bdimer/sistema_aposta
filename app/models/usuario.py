"""Modelo ORM que representa a tabela de usuários."""


from typing import TYPE_CHECKING
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Boolean, Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

# Este bloco não executa em produção; serve somente para editores e analisadores.
if TYPE_CHECKING:
    from app.models.aposta import Aposta


# Declara uma classe Python que o ORM mapeará para uma tabela SQL.
class Usuario(Base):
    """Armazena cadastro, autenticação, saldo e estado de participação."""

    # Define o nome real da tabela criada no banco.
    __tablename__ = "usuarios"
    # Cria a chave primária numérica preenchida automaticamente pelo banco.
    id: Mapped[int] = mapped_column(primary_key=True)
    # Armazena o nome do usuário com limite de 120 caracteres.
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    # Impede que duas contas tenham o mesmo e-mail.
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    # Impede CPFs repetidos e acelera consultas de validação.
    cpf: Mapped[str] = mapped_column(String(14), unique=True, index=True)
    # Guarda a data como tipo SQL DATE para permitir cálculo correto de idade.
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    # Define o identificador usado no login e exige unicidade.
    login: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    # Guarda somente o hash da senha, nunca a senha em texto puro.
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # Começa com exatamente 100 pontos e mantém duas casas decimais.
    saldo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("100.00"), nullable=False
    )
    # Permite inativar a conta sem remover seus dados históricos.
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Registra automaticamente quando a conta foi criada.
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Disponibiliza as apostas do usuário por meio do relacionamento ORM.
    apostas: Mapped[list["Aposta"]] = relationship(back_populates="usuario")
