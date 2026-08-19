
"""Processa resultados e liquida apostas em uma única transação."""

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.enums import (
    StatusAposta,
    StatusPartida,
)
from app.repositories.aposta_repository import (
    listar_apostas_pendentes_da_partida,
    usuario_possui_aposta_pendente,
)
from app.repositories.partida_repository import (
    buscar_partida_por_id,
)
from app.schemas.partida import (
    LiquidacaoResponse,
    ResultadoPartidaUpdate,
)


# Define duas casas decimais para prêmios e devoluções.
PRECISAO_PONTOS = Decimal("0.01")

# Cria um erro específico para resultados recusados.
class ErroRegraResultado(ValueError):
    """Representa uma liquidação recusada pelas regras do sistema."""

# Cria um erro controlado para falhas na transação.
class ErroPersistenciaResultado(RuntimeError):
    """Representa uma falha ao processar o resultado no banco."""


# Verifica se uma aposta acertou exatamente o placar.
def aposta_acertou_placar(
    aposta,
    gols_casa: int,
    gols_visitante: int,
) -> bool:
    """Retorna True somente quando os dois placares são iguais."""

    # Compara simultaneamente os gols da casa e do visitante.
    return (
        aposta.gols_casa == gols_casa
        and aposta.gols_visitante == gols_visitante
    )


# Calcula o prêmio bruto de uma aposta vencedora.
def calcular_premio(aposta) -> Decimal:
    """Multiplica o valor total pela ODD registrada."""

    # Aplica a fórmula definida pelas regras do sistema.
    premio = (
        aposta.valor_total
        * aposta.odd_registrada
    )
    # Arredonda o crédito para duas casas decimais.
    return premio.quantize(
        PRECISAO_PONTOS,
        rounding=ROUND_HALF_UP,
    )


# Atualiza o resultado e processa todas as apostas pendentes.
def liquidar_partida(
    database: Session,
    partida_id: int,
    dados: ResultadoPartidaUpdate,
) -> LiquidacaoResponse:
    """Finaliza uma partida e distribui pontos atomicamente."""

    partida = buscar_partida_por_id(
        database,
        partida_id,
    )
    if partida is None:
        raise ErroRegraResultado(
            "Partida não encontrada."
        )
    # Impede que a mesma partida seja liquidada mais de uma vez.
    if partida.status == StatusPartida.ENCERRADA:
        raise ErroRegraResultado(
            "Esta partida já foi encerrada."
        )
    # Impede a liquidação de uma partida cancelada.
    if partida.status == StatusPartida.CANCELADA:
        raise ErroRegraResultado(
            "Uma partida cancelada não pode receber resultado."
        )
    # Carrega todas as apostas que ainda aguardam resultado.
    apostas = listar_apostas_pendentes_da_partida(
        database,
        partida.id,
    )
    # Verifica se o placar real terminou empatado.
    resultado_empatado = (
        dados.gols_casa
        == dados.gols_visitante
    )
    # Inicializa os contadores do resumo.
    quantidade_vencedoras = 0
    quantidade_perdedoras = 0
    quantidade_devolvidas = 0
    quantidade_inativados = 0

    # Inicializa a soma de todos os créditos realizados.
    total_creditado = Decimal("0.00")
    # Guarda usuários afetados sem repetir o mesmo ID.
    usuarios_afetados = {}
    # Obtém um único horário para todas as apostas processadas.
    horario_liquidacao = datetime.now(
        timezone.utc
    )

    try:
        # Registra o placar final na partida.
        partida.gols_casa = dados.gols_casa
        partida.gols_visitante = dados.gols_visitante
        # Fecha a partida para impedir novas apostas.
        partida.status = StatusPartida.ENCERRADA
        database.add(partida)

        # Percorre todas as apostas pendentes.
        for aposta in apostas:
            usuario = aposta.usuario
            usuarios_afetados[usuario.id] = usuario

            aposta.liquidado_em = horario_liquidacao

            # Em empate real, todas as apostas são devolvidas.
            if resultado_empatado:
                # O crédito corresponde ao valor total apostado.
                valor_devolvido = aposta.valor_total
                # Devolve integralmente os pontos ao saldo.
                usuario.saldo += valor_devolvido
                # Registra quanto foi devolvido nesta aposta.
                aposta.premio = valor_devolvido
                # Marca a aposta como devolvida.
                aposta.status = StatusAposta.DEVOLVIDA
                # Incrementa o contador de devoluções.
                quantidade_devolvidas += 1
                # Soma a devolução ao total creditado.
                total_creditado += valor_devolvido

            # Fora de empate, verifica o placar exato.
            elif aposta_acertou_placar(
                aposta,
                dados.gols_casa,
                dados.gols_visitante,
            ):
                # Calcula o prêmio usando a ODD preservada.
                premio = calcular_premio(aposta)
                # Credita o prêmio no saldo do vencedor.
                usuario.saldo += premio
                # Registra o valor pago na aposta.
                aposta.premio = premio
                # Marca a aposta como vencedora.
                aposta.status = StatusAposta.VENCEDORA
                # Incrementa o contador de vencedoras.
                quantidade_vencedoras += 1
                # Soma o prêmio ao total creditado.
                total_creditado += premio

            # Executa este bloco quando o palpite está errado.
            else:
                # O débito já aconteceu durante o cadastro.
                aposta.premio = Decimal("0.00")
                # Marca o débito como perda definitiva.
                aposta.status = StatusAposta.PERDEDORA
                # Incrementa o contador de perdas.
                quantidade_perdedoras += 1

            database.add(aposta)
            database.add(usuario)
        database.flush()

        # Verifica falência somente depois de distribuir os resultados.
        for usuario in usuarios_afetados.values():
            # Consulta se o usuário possui outra aposta pendente.
            possui_pendente = usuario_possui_aposta_pendente(
                database,
                usuario.id,
            )
            # Inativa somente saldo zerado sem expectativa de crédito.
            if (
                usuario.saldo <= 0
                and not possui_pendente
                and usuario.ativo
            ):
                # Aplica a inativação por falência.
                usuario.ativo = False
                # Incrementa o contador de contas inativadas.
                quantidade_inativados += 1
                database.add(usuario)
        database.commit()

    except SQLAlchemyError as erro:
        database.rollback()
        raise ErroPersistenciaResultado(
            "Não foi possível liquidar a partida."
        ) from erro

    # Devolve um resumo validado do processamento.
    return LiquidacaoResponse(
        partida_id=partida.id,
        placar=(
            f"{dados.gols_casa}"
            f" x "
            f"{dados.gols_visitante}"
        ),
        apostas_vencedoras=quantidade_vencedoras,
        apostas_perdedoras=quantidade_perdedoras,
        apostas_devolvidas=quantidade_devolvidas,
        usuarios_inativados=quantidade_inativados,
        total_creditado=total_creditado,
    )