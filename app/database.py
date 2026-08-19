"""Configura a conexão, as sessões e a classe-base do SQLAlchemy."""

from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from app.config import settings

# SQLite precisa desta opção quando a mesma conexão atende diferentes requisições.
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)
# Cria o objeto central que administra as conexões com o banco SQL.
engine = create_engine(settings.database_url, connect_args=connect_args)
# Fabrica sessões; cada sessão representa uma unidade de trabalho com o banco.
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


# Todas as classes ORM herdarão desta base para entrar no catálogo do SQLAlchemy.
class Base(DeclarativeBase):
    """Classe-base compartilhada por todas as tabelas do projeto."""


# Declara uma dependência que abre uma sessão para cada requisição HTTP.
def get_db() -> Generator[Session, None, None]:
    """Entrega uma sessão e garante seu fechamento mesmo quando ocorre erro."""

    # Abre uma nova sessão ligada ao engine configurado acima.
    database = SessionLocal()
    # Inicia o bloco protegido que entregará a sessão ao código da rota.
    try:
        # yield pausa a função e disponibiliza a sessão para a requisição atual.
        yield database
    # finally sempre executa, com sucesso ou exceção durante a requisição.
    finally:
        # Devolve a conexão ao pool e evita vazamento de recursos.
        database.close()


# Encapsula a criação inicial das tabelas para facilitar testes e inicialização.
def create_database_tables() -> None:
    """Cria somente as tabelas que ainda não existem no banco configurado."""

    # Importa os modelos aqui para registrá-los na metadata antes do create_all.
    import app.models  # noqa: F401
    # Emite os comandos CREATE TABLE necessários sem apagar dados existentes.
    Base.metadata.create_all(bind=engine)
