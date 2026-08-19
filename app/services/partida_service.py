"""Implementa as regras de negócio relacionadas às partidas."""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.integrations.football_api import buscar_partidas_api
from app.models.enums import StatusPartida
from app.models.partida import Partida
from app.repositories.partida_repository import (
    adicionar_partida,
    atualizar_partida,
    buscar_partida_por_external_id,
    buscar_partida_por_id,
    listar_partidas,
)
from app.schemas.partida import SincronizacaoResponse


# Cria um erro específico para partidas inexistentes.
class ErroPartidaNaoEncontrada(ValueError):
    """Representa uma tentativa de acessar uma partida inexistente."""

# Cria um erro controlado para falhas de persistência.
class ErroPersistenciaPartida(RuntimeError):
    """Representa uma falha ao salvar ou atualizar partidas."""

# Importa partidas da API e salva ou atualiza cada registro.
def sincronizar_partidas(
    database: Session,
) -> SincronizacaoResponse:
    """Sincroniza partidas externas sem criar registros duplicados."""

    partidas_externas = buscar_partidas_api()
    quantidade_criada = 0
    quantidade_atualizada = 0

    try:
        # Percorre cada partida validada pelo Pydantic.
        for dados in partidas_externas:
            partida_existente = buscar_partida_por_external_id(
                database,
                dados.external_id,
            )

            if partida_existente is None:
                nova_partida = Partida(
                    external_id=dados.external_id,
                    time_casa=dados.time_casa,
                    time_visitante=dados.time_visitante,
                    inicio_em=dados.inicio_em,
                    fase=dados.fase,
                    status=dados.status,
                    gols_casa=dados.gols_casa,
                    gols_visitante=dados.gols_visitante,
                )

                adicionar_partida(
                    database,
                    nova_partida,
                )
                quantidade_criada += 1

            else:
                partida_existente.time_casa = dados.time_casa
                partida_existente.time_visitante = (
                    dados.time_visitante
                )

                # Atualiza a data e o horário da partida.
                partida_existente.inicio_em = dados.inicio_em
                # Atualiza a fase da competição.
                partida_existente.fase = dados.fase
                # Atualiza o estado recebido do provedor.
                partida_existente.status = dados.status
                # Atualiza o placar da casa, quando disponível.
                partida_existente.gols_casa = dados.gols_casa
                # Atualiza o placar visitante, quando disponível.
                partida_existente.gols_visitante = (
                    dados.gols_visitante
                )
                # Não altera as ODDs, pois elas pertencem ao nosso sistema.
                atualizar_partida(
                    database,
                    partida_existente,
                )
                # Registra que uma partida existente foi atualizada.
                quantidade_atualizada += 1
        # Confirma todas as inserções e atualizações juntas.
        database.commit()

    # Captura uma violação de identificador externo único.
    except IntegrityError as erro:
        database.rollback()

        # Entrega uma mensagem controlada para a futura rota.
        raise ErroPersistenciaPartida(
            "Uma partida externa já foi cadastrada."
        ) from erro

    # Captura outros problemas produzidos pelo SQLAlchemy.
    except SQLAlchemyError as erro:
        # Desfaz inserções e atualizações parciais.
        database.rollback()

        # Evita devolver detalhes internos do banco.
        raise ErroPersistenciaPartida(
            "Não foi possível sincronizar as partidas."
        ) from erro

    # Cria o resumo validado que será devolvido pela API.
    return SincronizacaoResponse(
        partidas_criadas=quantidade_criada,
        partidas_atualizadas=quantidade_atualizada,
    )

# Lista partidas armazenadas no banco.
def consultar_partidas(
    database: Session,
    status_partida: StatusPartida | None = None,
) -> list[Partida]:
    """Retorna partidas, aplicando um filtro opcional de status."""

    # Encaminha a consulta para o repositório.
    return listar_partidas(
        database,
        status_partida,
    )

# Obtém uma partida específica para consulta ou futura aposta.
def obter_partida(
    database: Session,
    partida_id: int,
) -> Partida:
    """Retorna uma partida ou gera um erro controlado."""

    # Procura a partida utilizando o identificador interno.
    partida = buscar_partida_por_id(
        database,
        partida_id,
    )
    # Interrompe a operação quando o ID não existe.
    if partida is None:
        raise ErroPartidaNaoEncontrada(
            "Partida não encontrada."
        )
    # Devolve a partida encontrada.
    return partida