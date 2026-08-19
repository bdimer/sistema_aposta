
"""Expõe operações administrativas protegidas por chave."""


from fastapi import APIRouter, HTTPException, status
from app.routes.dependencies import (
    AdminDependency,
    DatabaseDependency,
    UsuarioAtualDependency,
)
from app.schemas.aposta import (
    AdminApostaCreate,
    ApostaResponse,
)
from app.schemas.usuario import UsuarioResponse
from app.services.admin_service import (
    ErroRecursoAdmin,
    consultar_aposta_por_id,
    consultar_todos_usuarios,
    consultar_usuario_por_id,
    criar_aposta_administrativa,
)
from app.services.aposta_service import (
    ErroPersistenciaAposta,
    ErroRegraAposta,
)


# Cria um grupo de endpoints iniciado por /admin.
router = APIRouter(
    prefix="/admin",
    tags=["Administrador"],
)


# Lista todos os usuários do sistema.
@router.get(
    "/usuarios",
    response_model=list[UsuarioResponse],
)
def listar_usuarios(
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
    admin_key: AdminDependency,
) -> list[UsuarioResponse]:
    """Lista contas ativas e inativas para o administrador."""

    del usuario_atual
    del admin_key

    return consultar_todos_usuarios(database)


# Pesquisa um usuário específico.
@router.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResponse,
)
def pesquisar_usuario(
    usuario_id: int,
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
    admin_key: AdminDependency,
) -> UsuarioResponse:
    """Pesquisa dados de um usuário pelo ID."""

    del usuario_atual
    del admin_key

    try:
        return consultar_usuario_por_id(
            database,
            usuario_id,
        )

    except ErroRecursoAdmin as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro


# Cria uma aposta em nome do usuário informado.
@router.post(
    "/apostas",
    response_model=ApostaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_aposta_para_usuario(
    dados: AdminApostaCreate,
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
    admin_key: AdminDependency,
) -> ApostaResponse:
    """Registra uma aposta administrativa para um usuário."""

    del usuario_atual
    del admin_key

    try:
        return criar_aposta_administrativa(
            database,
            dados,
        )

    except ErroRecursoAdmin as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro

    except ErroRegraAposta as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro

    except ErroPersistenciaAposta as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(erro),
        ) from erro


# Pesquisa qualquer aposta pelo identificador.
@router.get(
    "/apostas/{aposta_id}",
    response_model=ApostaResponse,
)
def pesquisar_aposta(
    aposta_id: int,
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
    admin_key: AdminDependency,
) -> ApostaResponse:
    """Retorna os dados completos de uma aposta."""

    del usuario_atual
    del admin_key

    try:
        return consultar_aposta_por_id(
            database,
            aposta_id,
        )

    except ErroRecursoAdmin as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro