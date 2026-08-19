
"""Realiza a comunicação com a API externa Football Data."""


import logging
import requests
from pydantic import ValidationError
from app.config import settings
from app.models.enums import StatusPartida
from app.schemas.partida import PartidaImport


# Cria um registrador de mensagens específico para este módulo.
logger = logging.getLogger(__name__)

# Cria uma exceção específica para falhas da integração externa.
class ErroFootballAPI(RuntimeError):
    """Representa uma falha ao consultar ou interpretar a Football Data."""

# Converte o status externo para um status aceito pelo sistema.
def converter_status(status_externo: str) -> StatusPartida:
    """Traduz os diferentes estados retornados pela Football Data."""

    # Relaciona cada status externo ao equivalente interno.
    status_map = {
        "SCHEDULED": StatusPartida.AGENDADA,
        "TIMED": StatusPartida.AGENDADA,
        "IN_PLAY": StatusPartida.EM_ANDAMENTO,
        "PAUSED": StatusPartida.EM_ANDAMENTO,
        "FINISHED": StatusPartida.ENCERRADA,
        "AWARDED": StatusPartida.ENCERRADA,
        "SUSPENDED": StatusPartida.ADIADA,
        "POSTPONED": StatusPartida.ADIADA,
        "CANCELLED": StatusPartida.CANCELADA,
    }
    # Procura o status recebido dentro do dicionário.
    status_convertido = status_map.get(status_externo)

    # Interrompe a conversão quando o provedor envia um estado desconhecido.
    if status_convertido is None:
        raise ValueError(
            f"Status externo desconhecido: {status_externo}"
        )
    return status_convertido

# Converte uma partida bruta da API em um schema validado.
def converter_partida(
    dados_partida: dict,
) -> PartidaImport:
    """Transforma o JSON externo em dados internos padronizados."""

    # Obtém o objeto que contém o placar completo da partida.
    placar_final = dados_partida.get(
        "score",
        {},
    ).get(
        "fullTime",
        {},
    )
    # Obtém o nome do time da casa ou usa um texto temporário.
    time_casa = (
        dados_partida.get("homeTeam", {}).get("name")
        or "A definir"
    )
    # Obtém o nome do time visitante ou usa um texto temporário.
    time_visitante = (
        dados_partida.get("awayTeam", {}).get("name")
        or "A definir"
    )
    # Cria o schema Pydantic, que também validará todos os tipos.
    return PartidaImport(
        external_id=dados_partida["id"],
        time_casa=time_casa,
        time_visitante=time_visitante,
        inicio_em=dados_partida["utcDate"],
        fase=dados_partida.get("stage") or "Não informada",
        status=converter_status(
            dados_partida["status"]
        ),
        gols_casa=placar_final.get("home"),
        gols_visitante=placar_final.get("away"),
    )

# Consulta e valida as partidas disponíveis na Football Data.
def buscar_partidas_api() -> list[PartidaImport]:
    """Retorna partidas externas prontas para serem persistidas."""

    # Impede uma chamada inválida quando a chave não foi configurada.
    if not settings.football_api_key:
        raise ErroFootballAPI(
            "A variável API_KEY não foi configurada no arquivo .env."
        )
    # Junta a URL principal com o endpoint de partidas.
    url = (
        settings.football_base_url
        + settings.football_matches_endpoint
    )
    # Monta o cabeçalho de autenticação exigido pela Football Data.
    headers = {
        "X-Auth-Token": settings.football_api_key,
    }

    # Inicia o tratamento de erros da comunicação HTTP.
    try:
        # Realiza a requisição e limita o tempo de espera.
        response = requests.get(
            url,
            headers=headers,
            params={"season": 2026},
            timeout=settings.football_api_timeout,
        )
        # Gera uma exceção para respostas 400, 401, 403, 404 ou 500.
        response.raise_for_status()
        resposta_json = response.json()

    # Captura especificamente uma demora superior ao timeout.
    except requests.Timeout as erro:
        raise ErroFootballAPI(
            "A Football Data demorou demais para responder."
        ) from erro

    # Captura falhas de rede, DNS ou recusa de conexão.
    except requests.ConnectionError as erro:
        raise ErroFootballAPI(
            "Não foi possível conectar à Football Data."
        ) from erro

    # Captura códigos HTTP que representam erro.
    except requests.HTTPError as erro:
        # Obtém o código sem revelar a chave de autenticação.
        codigo = erro.response.status_code

        # Converte a falha externa em uma mensagem controlada.
        raise ErroFootballAPI(
            f"A Football Data respondeu com o código {codigo}."
        ) from erro

    # Captura outros erros produzidos pela biblioteca requests.
    except requests.RequestException as erro:
        raise ErroFootballAPI(
            "Ocorreu um erro ao consultar a Football Data."
        ) from erro

    # Captura uma resposta cujo corpo não seja um JSON válido.
    except ValueError as erro:
        raise ErroFootballAPI(
            "A Football Data devolveu uma resposta inválida."
        ) from erro

    # Obtém a lista de partidas presente no JSON.
    partidas_externas = resposta_json.get("matches")

    # Confirma que a resposta possui uma lista de partidas.
    if not isinstance(partidas_externas, list):
        raise ErroFootballAPI(
            "A resposta externa não contém uma lista de partidas."
        )
    partidas_validas: list[PartidaImport] = []

    # Percorre individualmente cada partida recebida.
    for dados_partida in partidas_externas:
        try:
            partidas_validas.append(
                converter_partida(dados_partida)
            )
        # Captura campos ausentes, tipos errados ou falhas do Pydantic.
        except (
            KeyError,
            TypeError,
            ValueError,
            ValidationError,
        ) as erro:
            # Registra o ID do item ignorado para facilitar a investigação.
            logger.warning(
                "Partida externa %s ignorada: %s",
                dados_partida.get("id", "sem ID"),
                erro,
            )
    return partidas_validas