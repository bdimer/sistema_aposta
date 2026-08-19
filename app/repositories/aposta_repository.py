"""Concentra as operações da tabela de apostas no banco de dados."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.enums import (
    SelecaoAposta,
    StatusAposta,
)
from app.models.aposta import Aposta


# Procura uma aposta pela chave primária.
def buscar_aposta_por_id(
    database: Session,
    aposta_id: int,
) -> Aposta | None:
    """Retorna a aposta do ID informado ou None."""

    # Monta uma consulta filtrando o identificador interno.
    consulta = select(Aposta).where(
        Aposta.id == aposta_id
    )
    return database.scalar(consulta)


# Procura uma aposta garantindo que ela pertença ao usuário.
def buscar_aposta_do_usuario(
    database: Session,
    aposta_id: int,
    usuario_id: int,
) -> Aposta | None:
    """Retorna somente uma aposta pertencente ao usuário informado."""

    consulta = select(Aposta).where(
        Aposta.id == aposta_id,
        Aposta.usuario_id == usuario_id,
    )
    return database.scalar(consulta)


# Lista todas as apostas de um usuário.
def listar_apostas_do_usuario(
    database: Session,
    usuario_id: int,
) -> list[Aposta]:
    """Retorna as apostas do usuário, começando pelas mais recentes."""

    # Seleciona somente apostas pertencentes ao usuário.
    consulta = (
        select(Aposta)
        .where(
            Aposta.usuario_id == usuario_id
        )
        .order_by(
            Aposta.criado_em.desc()
        )
    )
    resultado = database.scalars(consulta).all()
    return list(resultado)

# Conta quantas apostas pendentes existem em um lado da partida.
def contar_apostas_por_selecao(
    database: Session,
    partida_id: int,
    selecao: SelecaoAposta,
) -> int:
    """Conta apostas pendentes de casa, visitante ou empate."""

    # Monta um COUNT filtrado por partida, seleção e estado.
    consulta = select(
        func.count(Aposta.id)
    ).where(
        Aposta.partida_id == partida_id,
        Aposta.selecao == selecao,
        Aposta.status == StatusAposta.PENDENTE,
    )
    quantidade = database.scalar(consulta)
    # Usa zero como segurança caso o banco devolva None.
    return quantidade or 0


# Lista apostas pendentes de uma partida para futura liquidação.
def listar_apostas_pendentes_da_partida(
    database: Session,
    partida_id: int,
) -> list[Aposta]:
    """Retorna as apostas que ainda aguardam o resultado da partida."""

    # Filtra simultaneamente pela partida e pelo estado pendente.
    consulta = select(Aposta).where(
        Aposta.partida_id == partida_id,
        Aposta.status == StatusAposta.PENDENTE,
    )
    resultado = database.scalars(consulta).all()

    return list(resultado)


# Verifica se um usuário ainda possui alguma aposta pendente.
def usuario_possui_aposta_pendente(
    database: Session,
    usuario_id: int,
) -> bool:
    """Retorna True quando existe ao menos uma aposta não liquidada."""

    consulta = (
        select(Aposta.id)
        .where(
            Aposta.usuario_id == usuario_id,
            Aposta.status == StatusAposta.PENDENTE,
        )
        .limit(1)
    )
    aposta_id = database.scalar(consulta)
    return aposta_id is not None


# Adiciona uma aposta à transação atual.
def adicionar_aposta(
    database: Session,
    aposta: Aposta,
) -> Aposta:
    """Insere uma aposta sem confirmar definitivamente a transação."""

    database.add(aposta)
    database.flush()
    database.refresh(aposta)
    return aposta


# Envia alterações de uma aposta existente ao banco.
def atualizar_aposta(
    database: Session,
    aposta: Aposta,
) -> Aposta:
    """Sincroniza uma aposta alterada dentro da transação atual."""

    database.add(aposta)
    database.flush()
    database.refresh(aposta)
    return aposta



# Lista somente as apostas pendentes de um usuário.
def listar_apostas_ativas_do_usuario(
    database: Session,
    usuario_id: int,
) -> list[Aposta]:
    """Retorna apostas que ainda aguardam resultado."""

    consulta = (
        select(Aposta)
        .where(
            Aposta.usuario_id == usuario_id,
            Aposta.status == StatusAposta.PENDENTE,
        )
        .order_by(
            Aposta.criado_em.desc()
        )
    )

    resultado = database.scalars(consulta).all()
    return list(resultado)