
"""Expõe as funcionalidades de usuários através de endpoints HTTP."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.routes.dependencies import (
    DatabaseDependency,
    UsuarioAtualDependency,
)
from app.schemas.usuario import (
    SaldoResponse,
    TokenResponse,
    TrocaSenha,
    UsuarioCreate,
    UsuarioLogin,
    UsuarioResponse,
    RankingUsuarioResponse,
)
from app.services.security import criar_access_token
from app.services.usuario_service import (
    ErroPersistencia,
    ErroRegraNegocio,
    autenticar_usuario,
    cadastrar_usuario,
    inativar_usuario,
    trocar_senha,
    consultar_ranking,
)


# Cria um agrupador de endpoints com o prefixo /usuarios.
router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"],
)

# Registra uma rota POST para cadastrar contas.
@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_usuario(
    dados: UsuarioCreate,
    database: DatabaseDependency,
) -> UsuarioResponse:
    """Cadastra um usuário depois de validar os dados recebidos."""

    try:
        return cadastrar_usuario(
            database,
            dados,
        )

    except ErroRegraNegocio as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro

    except ErroPersistencia as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(erro),
        ) from erro



# Registra a rota que autentica o usuário.
@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    formulario: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    database: DatabaseDependency,
) -> TokenResponse:
    """Valida as credenciais e devolve um token JWT."""

    # Converte o formulário OAuth2 para o schema usado pelo serviço.
    dados_login = UsuarioLogin(
        login=formulario.username,
        senha=formulario.password,
    )

    # Inicia o tratamento dos possíveis erros de autenticação.
    try:
        usuario = autenticar_usuario(
            database,
            dados_login,
        )

    # Captura credenciais incorretas ou conta inativa.
    except ErroRegraNegocio as erro:
        # HTTP 401 informa que a autenticação não foi aceita.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(erro),
            headers={"WWW-Authenticate": "Bearer"},
        ) from erro

    access_token = criar_access_token(
        usuario.id
    )

    return TokenResponse(
        access_token=access_token,
    )


# Registra uma rota protegida para consultar a própria conta.
@router.get(
    "/me",
    response_model=UsuarioResponse,
)
def consultar_perfil(
    usuario_atual: UsuarioAtualDependency,
) -> UsuarioResponse:
    """Retorna os dados públicos do usuário autenticado."""

    # O usuário já foi validado pela dependência de autenticação.
    return usuario_atual


# Registra uma rota protegida dedicada ao saldo.
@router.get(
    "/me/saldo",
    response_model=SaldoResponse,
)
def consultar_saldo(
    usuario_atual: UsuarioAtualDependency,
) -> SaldoResponse:
    """Retorna os pontos disponíveis para novas apostas."""

    # Cria o schema de resposta sem expor outros dados da conta.
    return SaldoResponse(
        saldo=usuario_atual.saldo
    )


# Registra uma rota PATCH porque somente a senha será modificada.
@router.patch(
    "/me/senha",
    response_model=UsuarioResponse,
)
def alterar_senha(
    dados: TrocaSenha,
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
) -> UsuarioResponse:
    """Troca a senha da conta autenticada."""

    try:
        return trocar_senha(
            database,
            usuario_atual,
            dados,
        )

    except ErroRegraNegocio as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro

    except ErroPersistencia as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(erro),
        ) from erro


# Registra a rota que cancela a participação do usuário.
@router.patch(
    "/me/inativar",
    response_model=UsuarioResponse,
)
def cancelar_participacao(
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
) -> UsuarioResponse:
    """Inativa a conta sem excluir histórico, saldo ou apostas."""

    try:
        return inativar_usuario(
            database,
            usuario_atual,
        )

    except ErroRegraNegocio as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro

    except ErroPersistencia as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(erro),
        ) from erro


#------
# Cria o endpoint protegido da classificação geral.
@router.get(
    "/ranking",
    response_model=list[RankingUsuarioResponse],
)
def ranking(
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
) -> list[RankingUsuarioResponse]:
    """Lista a pontuação de usuários ativos e inativos."""

    del usuario_atual

    return consultar_ranking(database)