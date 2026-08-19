"""Expõe as funcionalidades de usuários através de endpoints HTTP."""

# Importa Annotated para declarar o formulário como dependência.
from typing import Annotated

# Importa os componentes usados para criar rotas e respostas HTTP.
from fastapi import APIRouter, Depends, HTTPException, status

# Importa o formulário padrão utilizado pelo OAuth2.
from fastapi.security import OAuth2PasswordRequestForm

# Importa as dependências de banco e usuário autenticado.
from app.routes.dependencies import (
    DatabaseDependency,
    UsuarioAtualDependency,
)

# Importa os schemas aceitos e devolvidos pelas rotas.
from app.schemas.usuario import (
    SaldoResponse,
    TokenResponse,
    TrocaSenha,
    UsuarioCreate,
    UsuarioLogin,
    UsuarioResponse,
)

# Importa a função que cria o token depois do login.
from app.services.security import criar_access_token

# Importa as regras de negócio de usuários.
from app.services.usuario_service import (
    ErroPersistencia,
    ErroRegraNegocio,
    autenticar_usuario,
    cadastrar_usuario,
    inativar_usuario,
    trocar_senha,
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

    # Inicia o tratamento dos erros conhecidos do serviço.
    try:
        # Envia o schema validado e a sessão para a regra de cadastro.
        return cadastrar_usuario(
            database,
            dados,
        )

    # Captura maioridade, senha inválida e dados duplicados.
    except ErroRegraNegocio as erro:
        # Responde com HTTP 400 porque os dados violam uma regra.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro

    # Captura falhas inesperadas ao gravar no banco.
    except ErroPersistencia as erro:
        # Responde sem revelar detalhes internos do banco.
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

    # Cria um JWT contendo o ID do usuário autenticado.
    access_token = criar_access_token(
        usuario.id
    )

    # Devolve o token no formato esperado pelo OAuth2.
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

    # Inicia o tratamento dos erros conhecidos da troca.
    try:
        # Executa a regra usando o usuário identificado pelo token.
        return trocar_senha(
            database,
            usuario_atual,
            dados,
        )

    # Captura senha atual incorreta ou nova senha insegura.
    except ErroRegraNegocio as erro:
        # Responde com HTTP 400 porque a operação foi recusada.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro

    # Captura falhas inesperadas durante a atualização.
    except ErroPersistencia as erro:
        # Responde com erro interno sem expor comandos SQL.
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

    # Inicia o tratamento dos erros da inativação.
    try:
        # Altera o campo ativo e confirma a transação.
        return inativar_usuario(
            database,
            usuario_atual,
        )

    # Captura uma tentativa de inativar uma conta já inativa.
    except ErroRegraNegocio as erro:
        # Responde com HTTP 400 para a operação inválida.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro

    # Captura falhas inesperadas na persistência.
    except ErroPersistencia as erro:
        # Responde com uma mensagem controlada.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(erro),
        ) from erro