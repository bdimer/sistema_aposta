"""Concentra as operações da tabela de partidas no banco de dados."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.enums import StatusPartida
from app.models.partida import Partida

# Procura uma partida pela chave primária interna.
def buscar_partida_por_id(
    database: Session,
    partida_id: int,
) -> Partida | None:
    """Retorna a partida do ID informado ou None."""

    consulta = select(Partida).where(
        Partida.id == partida_id
    )

    # Executa a consulta e retorna uma partida ou None.
    return database.scalar(consulta)


# Procura uma partida pelo identificador da API externa.
def buscar_partida_por_external_id(
    database: Session,
    external_id: int,
) -> Partida | None:
    """Retorna a partida do ID externo informado ou None."""

    # Monta uma consulta utilizando o ID da Football Data.
    consulta = select(Partida).where(
        Partida.external_id == external_id
    )

    return database.scalar(consulta)


def listar_partidas(
    database: Session,
    status_partida: StatusPartida | None = None,
) -> list[Partida]:
    """Lista partidas, permitindo filtrar por status."""

    # Cria inicialmente uma consulta que seleciona todas as partidas.
    consulta = select(Partida)
    
    if status_partida is not None:
        # Restringe os resultados ao estado recebido.
        consulta = consulta.where(
            Partida.status == status_partida
        )

    consulta = consulta.order_by(
        Partida.inicio_em
    )
    # Executa a consulta e obtém os objetos SQLAlchemy.
    resultado = database.scalars(consulta).all()
    return list(resultado)


# Adiciona uma partida à transação atual.
def adicionar_partida(
    database: Session,
    partida: Partida,
) -> Partida:
    """Adiciona uma partida sem confirmar definitivamente a transação."""

    database.add(partida)
    # Executa o INSERT e permite obter o ID criado pelo banco.
    database.flush()
    database.refresh(partida)
    return partida


# Envia modificações de uma partida existente ao banco.
def atualizar_partida(
    database: Session,
    partida: Partida,
) -> Partida:
    """Sincroniza alterações sem confirmar definitivamente a transação."""

    database.add(partida)
    # Executa o UPDATE necessário dentro da transação atual.
    database.flush()
    # Recarrega o estado da partida depois da atualização.
    database.refresh(partida)
    return partida