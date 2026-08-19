"""Cria a aplicação HTTP e inicializa a estrutura do banco de dados."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.database import create_database_tables
from app.routes.partida_routes import router as partida_router
from app.routes.usuario_routes import router as usuario_router
from app.routes.aposta_routes import router as aposta_router


# Converte a função em um gerenciador do ciclo de vida da aplicação.
@asynccontextmanager
# Recebe a aplicação iniciada, embora ainda não seja necessário usá-la diretamente.
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Prepara o banco antes de aceitar requisições HTTP."""

    # Evita alerta de variável ainda não usada durante esta primeira fase.
    del application
    create_database_tables()
    # Entrega o controle ao FastAPI enquanto o servidor estiver executando.
    yield


# Instancia a API com nome, versão e rotina de inicialização.
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

# Adiciona todas as rotas de usuários à aplicação principal.
app.include_router(usuario_router)
app.include_router(partida_router)
app.include_router(aposta_router)

@app.get("/health", tags=["Sistema"])

def health_check() -> dict[str, str]:
    """Retorna o estado básico da aplicação sem consultar dados privados."""

    return {"status": "ok"}
