
"""Implementa operações permitidas somente ao administrador."""


from sqlalchemy.orm import Session
from app.models.aposta import Aposta
from app.models.usuario import Usuario
from app.repositories.aposta_repository import (
    buscar_aposta_por_id,
)
from app.repositories.usuario_repository import (
    buscar_usuario_por_id,
    listar_todos_usuarios,
)
from app.schemas.aposta import (
    AdminApostaCreate,
    ApostaCreate,
)
from app.services.aposta_service import criar_aposta


# Define um erro para recursos administrativos inexistentes.
class ErroRecursoAdmin(ValueError):
    """Representa um usuário ou aposta não encontrado."""


# Lista todos os usuários cadastrados.
def consultar_todos_usuarios(
    database: Session,
) -> list[Usuario]:
    """Retorna usuários ativos e inativos para o administrador."""

    return listar_todos_usuarios(database)


# Pesquisa os dados de um usuário específico.
def consultar_usuario_por_id(
    database: Session,
    usuario_id: int,
) -> Usuario:
    """Retorna o usuário ou gera um erro controlado."""

    usuario = buscar_usuario_por_id(
        database,
        usuario_id,
    )

    if usuario is None:
        raise ErroRecursoAdmin(
            "Usuário não encontrado."
        )

    return usuario


# Registra uma aposta em nome de um usuário escolhido.
def criar_aposta_administrativa(
    database: Session,
    dados: AdminApostaCreate,
) -> Aposta:
    """Cria uma aposta para um usuário usando as regras normais."""

    usuario = buscar_usuario_por_id(
        database,
        dados.usuario_id,
    )

    if usuario is None:
        raise ErroRecursoAdmin(
            "Usuário não encontrado."
        )

    # Converte o schema administrativo para o schema comum.
    dados_aposta = ApostaCreate(
        partida_id=dados.partida_id,
        gols_casa=dados.gols_casa,
        gols_visitante=dados.gols_visitante,
        valor_apostado=dados.valor_apostado,
    )

    return criar_aposta(
        database,
        usuario,
        dados_aposta,
    )


# Pesquisa qualquer aposta utilizando seu identificador.
def consultar_aposta_por_id(
    database: Session,
    aposta_id: int,
) -> Aposta:
    """Retorna uma aposta ou gera um erro controlado."""

    aposta = buscar_aposta_por_id(
        database,
        aposta_id,
    )
    if aposta is None:
        raise ErroRecursoAdmin(
            "Aposta não encontrada."
        )

    return aposta