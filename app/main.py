"""Cria a aplicação HTTP e inicializa a estrutura do banco de dados."""

# Importa AsyncIterator para documentar o tipo do ciclo de vida assíncrono.
from collections.abc import AsyncIterator
# Importa asynccontextmanager para executar ações ao iniciar e encerrar a API.
from contextlib import asynccontextmanager
# Importa FastAPI, classe central que recebe configuração e registra rotas.
from fastapi import FastAPI
# Importa as configurações e a função que cria tabelas ausentes.
from app.config import settings
from app.database import create_database_tables
from app.routes.usuario_routes import router as usuario_router


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

# Registra uma rota GET simples usada para confirmar que o backend está vivo.
@app.get("/health", tags=["Sistema"])
# Define o tipo exato da resposta, permitindo validação automática pelo FastAPI.
def health_check() -> dict[str, str]:
    """Retorna o estado básico da aplicação sem consultar dados privados."""

    # Devolve um dicionário que o FastAPI transforma automaticamente em JSON.
    return {"status": "ok"}
