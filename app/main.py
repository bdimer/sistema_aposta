"""Cria a aplicação HTTP e inicializa a estrutura do banco de dados."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import settings
from app.database import create_database_tables
from app.routes.partida_routes import router as partida_router
from app.routes.usuario_routes import router as usuario_router
from app.routes.aposta_routes import router as aposta_router
from app.routes.admin_routes import router as admin_router


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

# Localiza os arquivos do frontend a partir da pasta deste módulo.
FRONTEND_DIR = Path(__file__).resolve().parent / "static"

# Disponibiliza CSS e JavaScript no mesmo servidor da API.
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Adiciona todas as rotas de usuários à aplicação principal.
app.include_router(usuario_router)
app.include_router(partida_router)
app.include_router(aposta_router)
app.include_router(admin_router)


@app.get("/", include_in_schema=False)
def pagina_inicial() -> FileResponse:
    """Entrega a interface visual usada na demonstração."""

    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/health", tags=["Sistema"])

def health_check() -> dict[str, str]:
    """Retorna o estado básico da aplicação sem consultar dados privados."""

    return {"status": "ok"}
