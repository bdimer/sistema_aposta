"""Expõe as funcionalidades de partidas através de endpoints HTTP."""

from fastapi import APIRouter, HTTPException, Query, status
from app.integrations.football_api import ErroFootballAPI
from app.models.enums import StatusPartida
from app.routes.dependencies import (
    DatabaseDependency,
    UsuarioAtualDependency,
)
from app.schemas.partida import (
    PartidaResponse,
    SincronizacaoResponse,
)
from app.services.partida_service import (
    ErroPartidaNaoEncontrada,
    ErroPersistenciaPartida,
    consultar_partidas,
    obter_partida,
    sincronizar_partidas,
)

# Cria um grupo de rotas iniciado por /partidas.
router = APIRouter(
    prefix="/partidas",
    tags=["Partidas"],
)
# Cria o endpoint que atualiza o banco usando a Football Data.
@router.post(
    "/sincronizar",
    response_model=SincronizacaoResponse,
)
def sincronizar(
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
) -> SincronizacaoResponse:
    """Importa ou atualiza partidas utilizando a API externa."""

    # A variável comprova que a rota exigiu autenticação.
    del usuario_atual

    try:
        return sincronizar_partidas(database)
    # Captura ausência de chave, falha de rede ou resposta externa inválida.
    except ErroFootballAPI as erro:
        # HTTP 502 indica falha em um serviço externo utilizado pela API.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(erro),
        ) from erro
    except ErroPersistenciaPartida as erro:
        # Responde com erro interno sem revelar comandos SQL.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(erro),
        ) from erro

# Cria o endpoint que lista partidas armazenadas.
@router.get(
    "",
    response_model=list[PartidaResponse],
)
def listar(
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
    status_partida: StatusPartida | None = Query(
        default=None,
        alias="status",
    ),
) -> list[PartidaResponse]:
    """Lista partidas com filtro opcional de status."""
    # A presença desta variável garante que o usuário está autenticado.
    del usuario_atual
    # Consulta o banco usando o filtro recebido pela URL.
    return consultar_partidas(
        database,
        status_partida,
    )

# Cria o endpoint que consulta uma única partida.
@router.get(
    "/{partida_id}",
    response_model=PartidaResponse,
)
def consultar(
    partida_id: int,
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
) -> PartidaResponse:
    """Retorna uma partida usando seu identificador interno."""

    del usuario_atual
    try:
        return obter_partida(
            database,
            partida_id,
        )

    # Captura IDs que não correspondam a nenhuma partida.
    except ErroPartidaNaoEncontrada as erro:
        # HTTP 404 informa que o recurso solicitado não existe.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro