
"""Configura um banco temporário e um cliente HTTP para os testes."""


from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker
from app.database import Base, get_db
from app.main import app
#módulo foi importado intencionalmente para registrar as tabelas, mesmo sem ser usado diretamente
from app import models as _models  # noqa: F401


# Cria um banco SQLite somente em memória.
test_engine = create_engine(
    "sqlite://",

    # Permite que o cliente HTTP e o teste compartilhem a conexão.
    connect_args={
        "check_same_thread": False,
    },

    # Mantém uma única conexão enquanto o teste estiver executando.
    poolclass=StaticPool,
)

# Cria uma fábrica de sessões ligada ao banco temporário.
TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


# Cria uma sessão limpa para cada função de teste.
@pytest.fixture
def database() -> Generator[Session, None, None]:
    """Entrega um banco vazio e o destrói depois do teste."""

    # Cria todas as tabelas no banco temporário.
    Base.metadata.create_all(
        bind=test_engine
    )

    # Abre uma sessão exclusiva para o teste atual.
    session = TestSessionLocal()

    try:
        # Entrega a sessão para o teste.
        yield session

    # Este bloco sempre é executado ao final.
    finally:
        # Fecha a sessão utilizada pelo teste.
        session.close()
        # Remove todas as tabelas e seus dados temporários.
        Base.metadata.drop_all(
            bind=test_engine
        )


# Cria um cliente FastAPI que utiliza o banco temporário.
@pytest.fixture
def client(
    database: Session,
) -> Generator[TestClient, None, None]:
    """Entrega um cliente HTTP isolado do banco real."""

    # Substitui a dependência original de banco.
    def override_get_db() -> Generator[Session, None, None]:
        """Entrega a sessão temporária às rotas testadas."""

        # Disponibiliza exatamente a sessão criada pela fixture.
        yield database

    # Registra a substituição dentro do FastAPI.
    app.dependency_overrides[get_db] = (
        override_get_db
    )
    # Cria o cliente que fará requisições sem iniciar o Uvicorn.
    test_client = TestClient(app)

    # Inicia o bloco protegido do cliente.
    try:
        yield test_client

    # Executa depois que o teste terminar.
    finally:
        # Remove as substituições para não afetar outros testes.
        app.dependency_overrides.clear()