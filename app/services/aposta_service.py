
"""Implementa as regras de negócio relacionadas às apostas."""

from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.enums import (
    SelecaoAposta,
    StatusAposta,
    StatusPartida,
)
from app.models.aposta import Aposta
from app.models.usuario import Usuario
from app.repositories.aposta_repository import (
    adicionar_aposta,
    atualizar_aposta,
    buscar_aposta_do_usuario,
    contar_apostas_por_selecao,
    listar_apostas_do_usuario,
)
from app.repositories.partida_repository import (
    atualizar_partida,
    buscar_partida_por_id,
)
from app.schemas.aposta import (
    ApostaCreate,
    MultiplicacaoAposta,
)

# Definido quatro casas decimais para as ODDs.
PRECISAO_ODD = Decimal("0.0001")

class ErroRegraAposta(ValueError):
    """Representa uma aposta recusada pelas regras do sistema."""

class ErroPersistenciaAposta(RuntimeError):
    """Representa uma falha ao salvar ou atualizar uma aposta."""


# Descobre qual resultado o placar informado representa.
def identificar_selecao(
    gols_casa: int,
    gols_visitante: int,
) -> SelecaoAposta:
    """Converte o placar previsto em casa, visitante ou empate."""

    # Verifica se o palpite prevê vitória do time da casa.
    if gols_casa > gols_visitante:
        return SelecaoAposta.CASA

    # Verifica se o palpite prevê vitória do visitante.
    if gols_visitante > gols_casa:
        return SelecaoAposta.VISITANTE
    
    return SelecaoAposta.EMPATE


# Escolhe a ODD que será preservada na nova aposta.
def obter_odd_atual(
    partida,
    selecao: SelecaoAposta,
) -> Decimal:
    """Retorna a ODD exibida antes do cadastro da aposta."""

    # Usa a ODD da casa quando o placar favorece o mandante.
    if selecao == SelecaoAposta.CASA:
        return partida.odd_casa
    # Usa a ODD visitante quando o placar favorece o visitante.
    if selecao == SelecaoAposta.VISITANTE:
        return partida.odd_visitante
    # Empates são devolvidos e, portanto, não possuem prêmio por ODD.
    return Decimal("1.0000")

# Recalcula as ODDs que valerão para as próximas apostas.
def recalcular_odds(
    database: Session,
    partida,
) -> None:
    """Atualiza as ODDs usando as apostas pendentes de cada lado."""

    # Conta as apostas que apontam vitória da casa.
    quantidade_casa = contar_apostas_por_selecao(
        database,
        partida.id,
        SelecaoAposta.CASA,
    )
    # Conta as apostas que apontam vitória do visitante.
    quantidade_visitante = contar_apostas_por_selecao(
        database,
        partida.id,
        SelecaoAposta.VISITANTE,
    )
    # Aplica a ODD padrão se algum dos lados ainda estiver zerado.
    if quantidade_casa == 0 or quantidade_visitante == 0:
        partida.odd_casa = Decimal("2.0000")
        partida.odd_visitante = Decimal("2.0000")

    # Executa as fórmulas quando os dois lados possuem apostas.
    else:
        casa_decimal = Decimal(quantidade_casa)
        visitante_decimal = Decimal(
            quantidade_visitante
        )
        # Calcula a proporção inversa da ODD da casa.
        odd_casa = Decimal("1") + (
            visitante_decimal / casa_decimal
        )
        # Calcula a proporção inversa da ODD visitante.
        odd_visitante = Decimal("1") + (
            casa_decimal / visitante_decimal
        )
        # Arredonda a ODD da casa para quatro casas.
        partida.odd_casa = odd_casa.quantize(
            PRECISAO_ODD,
            rounding=ROUND_HALF_UP,
        )
        # Arredonda a ODD visitante para quatro casas.
        partida.odd_visitante = odd_visitante.quantize(
            PRECISAO_ODD,
            rounding=ROUND_HALF_UP,
        )
    atualizar_partida(
        database,
        partida,
    )

# Registra uma aposta e debita o saldo na mesma transação.
def criar_aposta(
    database: Session,
    usuario: Usuario,
    dados: ApostaCreate,
) -> Aposta:
    """Valida, debita, registra e recalcula as ODDs."""

    # Impede operações de uma conta inativa.
    if not usuario.ativo:
        raise ErroRegraAposta(
            "Usuário inativo."
        )
    # Procura a partida escolhida pelo usuário.
    partida = buscar_partida_por_id(
        database,
        dados.partida_id,
    )
    # Interrompe a operação se a partida não existir.
    if partida is None:
        raise ErroRegraAposta(
            "Partida não encontrada."
        )
    # Permite apostas somente enquanto a partida estiver agendada.
    if partida.status != StatusPartida.AGENDADA:
        raise ErroRegraAposta(
            "Esta partida não está disponível para apostas."
        )
    # Confirma que o usuário possui pontos suficientes.
    if dados.valor_apostado > usuario.saldo:
        raise ErroRegraAposta(
            "Saldo insuficiente para realizar a aposta."
        )
    # Descobre o lado representado pelo placar previsto.
    selecao = identificar_selecao(
        dados.gols_casa,
        dados.gols_visitante,
    )
    # Captura a ODD atual antes que esta aposta altere as proporções.
    odd_registrada = obter_odd_atual(
        partida,
        selecao,
    )
    # Cria o objeto ORM que representa a nova aposta.
    nova_aposta = Aposta(
        usuario_id=usuario.id,
        partida_id=partida.id,
        gols_casa=dados.gols_casa,
        gols_visitante=dados.gols_visitante,
        selecao=selecao,
        valor_base=dados.valor_apostado,
        multiplicador=1,
        odd_registrada=odd_registrada,
    )
    # Inicia o tratamento da transação financeira.
    try:
        usuario.saldo -= dados.valor_apostado
        database.add(usuario)
        adicionar_aposta(
            database,
            nova_aposta,
        )
        recalcular_odds(
            database,
            partida,
        )
        database.commit()
        database.refresh(nova_aposta)
        return nova_aposta

    except SQLAlchemyError as erro:
        database.rollback()
        raise ErroPersistenciaAposta(
            "Não foi possível registrar a aposta."
        ) from erro


# Multiplica uma aposta existente e debita somente a diferença.
def multiplicar_aposta(
    database: Session,
    usuario: Usuario,
    aposta_id: int,
    dados: MultiplicacaoAposta,
) -> Aposta:
    """Aplica um fator de x2 a x5 sobre uma aposta pendente."""

    # Procura a aposta e confirma que pertence ao usuário.
    aposta = buscar_aposta_do_usuario(
        database,
        aposta_id,
        usuario.id,
    )
    # Impede acesso a uma aposta inexistente ou pertencente a outra conta.
    if aposta is None:
        raise ErroRegraAposta(
            "Aposta não encontrada."
        )

    # Impede alterações depois da liquidação.
    if aposta.status != StatusAposta.PENDENTE:
        raise ErroRegraAposta(
            "Somente apostas pendentes podem ser multiplicadas."
        )
    # Procura a partida associada à aposta.
    partida = buscar_partida_por_id(
        database,
        aposta.partida_id,
    )
    # Protege contra uma referência inválida no banco.
    if partida is None:
        raise ErroRegraAposta(
            "Partida da aposta não encontrada."
        )
    # Impede multiplicação depois do fechamento das apostas.
    if partida.status != StatusPartida.AGENDADA:
        raise ErroRegraAposta(
            "A partida não aceita mais multiplicações."
        )
    # Guarda o valor total antes da multiplicação.
    valor_total_atual = aposta.valor_total
    # Calcula o novo fator acumulado.
    novo_multiplicador = (
        aposta.multiplicador
        * dados.multiplicador
    )
    # Calcula o novo valor total comprometido.
    novo_valor_total = (
        aposta.valor_base
        * novo_multiplicador
    )
    # Calcula apenas os pontos adicionais que serão debitados.
    valor_adicional = (
        novo_valor_total
        - valor_total_atual
    )
    # Confirma que o usuário possui o valor adicional.
    if valor_adicional > usuario.saldo:
        raise ErroRegraAposta(
            "Saldo insuficiente para multiplicar a aposta."
        )

    # Inicia o tratamento da atualização financeira.
    try:
        usuario.saldo -= valor_adicional
        aposta.multiplicador = novo_multiplicador
        database.add(usuario)
        atualizar_aposta(
            database,
            aposta,
        )
        database.commit()
        database.refresh(aposta)
        return aposta

    # Captura falhas durante a atualização.
    except SQLAlchemyError as erro:
        database.rollback()
        raise ErroPersistenciaAposta(
            "Não foi possível multiplicar a aposta."
        ) from erro


# Consulta as apostas pertencentes ao usuário autenticado.
def consultar_apostas_usuario(
    database: Session,
    usuario: Usuario,
) -> list[Aposta]:
    """Lista somente as apostas do usuário recebido."""

    return listar_apostas_do_usuario(
        database,
        usuario.id,
    )