"""Expõe as funcionalidades de apostas através de endpoints HTTP."""

from fastapi import APIRouter, HTTPException, status
from app.routes.dependencies import (
    DatabaseDependency,
    UsuarioAtualDependency,
)
from app.schemas.aposta import (
    ApostaCreate,
    ApostaResponse,
    MultiplicacaoAposta,
)
from app.services.aposta_service import (
    ErroPersistenciaAposta,
    ErroRegraAposta,
    consultar_apostas_usuario,
    criar_aposta,
    multiplicar_aposta,
    consultar_apostas_ativas_usuario,
)

# Cria um grupo de endpoints iniciado por /apostas.
router = APIRouter(
    prefix="/apostas",
    tags=["Apostas"],
)

# Registra uma nova aposta para o usuário autenticado.
@router.post(
    "",
    response_model=ApostaResponse,
    status_code=status.HTTP_201_CREATED,
)
def apostar(
    dados: ApostaCreate,
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
) -> ApostaResponse:
    """Registra uma aposta e debita seu valor do saldo."""

    try:
        return criar_aposta(
            database,
            usuario_atual,
            dados,
        )
    
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


# Lista todas as apostas do usuário autenticado.
@router.get(
    "/minhas",
    response_model=list[ApostaResponse],
)
def listar_minhas_apostas(
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
) -> list[ApostaResponse]:
    """Retorna somente as apostas pertencentes ao usuário atual."""

    return consultar_apostas_usuario(
        database,
        usuario_atual,
    )


# Lista somente as apostas que ainda aguardam resultado.
@router.get(
    "/minhas/ativas",
    response_model=list[ApostaResponse],
)
def listar_minhas_apostas_ativas(
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
) -> list[ApostaResponse]:
    """Retorna somente apostas com status PENDING."""

    return consultar_apostas_ativas_usuario(
        database,
        usuario_atual,
    )



# Multiplica uma aposta pendente por um fator de x2 a x5.
@router.patch(
    "/{aposta_id}/multiplicar",
    response_model=ApostaResponse,
)
def multiplicar(
    aposta_id: int,
    dados: MultiplicacaoAposta,
    database: DatabaseDependency,
    usuario_atual: UsuarioAtualDependency,
) -> ApostaResponse:
    """Multiplica o valor total de uma aposta existente."""

    try:
        return multiplicar_aposta(
            database,
            usuario_atual,
            aposta_id,
            dados,
        )

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