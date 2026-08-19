"""Prepara partidas previsíveis para a apresentação do projeto."""


from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.database import SessionLocal, create_database_tables
from app.models import Partida, StatusPartida


# Reúne os dados das partidas utilizadas durante a apresentação.
PARTIDAS_APRESENTACAO = [
    {
        # Identificador fictício que simula o código da API externa.
        "external_id": 800_000_001,
        # Define o time que jogou em casa.
        "time_casa": "Brasil",
        # Define o time visitante.
        "time_visitante": "México",
        # Coloca a partida dois dias antes do momento atual.
        "dias": -2,
        # Identifica a finalidade desse registro.
        "fase": "APRESENTAÇÃO - RESULTADO DISPONÍVEL",
        # Informa que essa partida já terminou.
        "status": StatusPartida.ENCERRADA,
        # Define o placar final do time da casa.
        "gols_casa": 2,
        # Define o placar final do time visitante.
        "gols_visitante": 0,
    },
    {
        # Usa outro identificador externo único.
        "external_id": 800_000_003,
        # Define o time da casa da partida que receberá apostas.
        "time_casa": "França",
        # Define o time visitante da partida que receberá apostas.
        "time_visitante": "Alemanha",
        # Agenda a partida para três dias depois do momento atual.
        "dias": 3,
        # Identifica o cenário principal da demonstração.
        "fase": "APRESENTAÇÃO - APOSTAS",
        # Mantém a partida aberta para receber apostas.
        "status": StatusPartida.AGENDADA,
        # Não existe placar enquanto a partida não for encerrada.
        "gols_casa": None,
        # Não existe placar enquanto a partida não for encerrada.
        "gols_visitante": None,
    },
    {
        # Mantém um identificador exclusivo para o cenário de falência.
        "external_id": 800_000_004,
        # Define o time da casa do cenário opcional.
        "time_casa": "Japão",
        # Define o time visitante do cenário opcional.
        "time_visitante": "Espanha",
        # Agenda essa partida depois do cenário principal.
        "dias": 4,
        # Identifica rapidamente a finalidade durante a apresentação.
        "fase": "APRESENTAÇÃO - FALÊNCIA",
        # Permite que a partida receba apostas.
        "status": StatusPartida.AGENDADA,
        # Mantém o placar vazio até o fechamento administrativo.
        "gols_casa": None,
        # Mantém o placar visitante vazio até o fechamento.
        "gols_visitante": None,
    },
    {
        # Mantém um identificador exclusivo para o cenário de empate.
        "external_id": 800_000_005,
        # Define o time da casa do segundo cenário opcional.
        "time_casa": "Portugal",
        # Define o time visitante do segundo cenário opcional.
        "time_visitante": "Países Baixos",
        # Agenda a partida para depois dos outros cenários.
        "dias": 5,
        # Identifica o teste opcional de devolução dos pontos.
        "fase": "APRESENTAÇÃO - EMPATE",
        # Mantém a partida aberta para novas apostas.
        "status": StatusPartida.AGENDADA,
        # Não define gols antes do encerramento.
        "gols_casa": None,
        # Não define gols visitantes antes do encerramento.
        "gols_visitante": None,
    },
]


# Define a função responsável por cadastrar os cenários.
def preparar_apresentacao() -> None:
    """Cria as partidas da apresentação sem gerar duplicações."""

    # Garante que as tabelas existam antes de abrir as consultas.
    create_database_tables()

    # Abre uma unidade de trabalho com o banco de dados.
    database = SessionLocal()

    # Inicia o bloco protegido da transação.
    try:
        # Percorre cada dicionário configurado anteriormente.
        for dados in PARTIDAS_APRESENTACAO:
            # Monta uma consulta pelo identificador externo.
            consulta = select(Partida).where(
                Partida.external_id == dados["external_id"]
            )

            # Executa a consulta e retorna um registro ou None.
            partida_existente = database.scalar(consulta)

            # Verifica se o cenário já foi criado anteriormente.
            if partida_existente is not None:
                # Exibe o ID que será utilizado no Swagger.
                print(
                    f"Partida já existente: {partida_existente.id} - "
                    f"{partida_existente.time_casa} x "
                    f"{partida_existente.time_visitante}"
                )

                # Pula para o próximo cenário sem duplicar o registro.
                continue

            # Calcula uma data passada ou futura conforme o cenário.
            inicio_em = datetime.now(timezone.utc) + timedelta(
                days=dados["dias"]
            )

            # Cria o objeto que será persistido na tabela de partidas.
            partida = Partida(
                external_id=dados["external_id"],
                time_casa=dados["time_casa"],
                time_visitante=dados["time_visitante"],
                inicio_em=inicio_em,
                fase=dados["fase"],
                status=dados["status"],
                gols_casa=dados["gols_casa"],
                gols_visitante=dados["gols_visitante"],
            )

            # Adiciona a nova partida à transação atual.
            database.add(partida)

            # Envia temporariamente o INSERT para obter o ID.
            database.flush()

            # Mostra no terminal o ID criado para a apresentação.
            print(
                f"Partida criada: {partida.id} - "
                f"{partida.time_casa} x {partida.time_visitante}"
            )

        # Confirma todas as inserções de uma única vez.
        database.commit()

    # Captura qualquer erro ocorrido durante a preparação.
    except Exception:
        # Desfaz todas as operações ainda não confirmadas.
        database.rollback()

        # Reenvia a exceção para mostrar sua causa no terminal.
        raise

    # Este bloco executa tanto em caso de sucesso quanto de erro.
    finally:
        # Fecha a sessão e libera sua conexão.
        database.close()


# Verifica se o arquivo foi executado diretamente pelo terminal.
if __name__ == "__main__":
    # Inicia a preparação das partidas.
    preparar_apresentacao()
