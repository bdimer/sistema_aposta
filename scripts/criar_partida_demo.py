"""Cria partidas futuras para testar os principais cenários do sistema."""

# Importa recursos para gerar datas futuras.
from datetime import datetime, timedelta, timezone

# Importa select para evitar partidas duplicadas.
from sqlalchemy import select

# Importa a fábrica de sessões.
from app.database import SessionLocal

# Importa o modelo e o status das partidas.
from app.models import Partida, StatusPartida


# Define os cenários que serão criados no banco.
CENARIOS = [
    {
        "external_id": 999_999_999,
        "time_casa": "Brasil",
        "time_visitante": "Argentina",
        "fase": "DEMONSTRAÇÃO - EMPATE",
        "dias": 7,
    },
    {
        "external_id": 999_999_998,
        "time_casa": "França",
        "time_visitante": "Alemanha",
        "fase": "DEMONSTRAÇÃO - VITÓRIA",
        "dias": 8,
    },
    {
        "external_id": 999_999_997,
        "time_casa": "Japão",
        "time_visitante": "Espanha",
        "fase": "DEMONSTRAÇÃO - FALÊNCIA",
        "dias": 9,
    },
]


# Cria somente os cenários que ainda não existem.
def criar_partidas_demo() -> None:
    """Insere partidas de teste sem duplicar registros existentes."""

    # Abre uma sessão com o banco.
    database = SessionLocal()

    # Inicia o tratamento da transação.
    try:
        # Percorre cada cenário definido acima.
        for cenario in CENARIOS:
            # Procura uma partida com o mesmo ID externo.
            consulta = select(Partida).where(
                Partida.external_id
                == cenario["external_id"]
            )

            # Executa a consulta de existência.
            partida_existente = database.scalar(
                consulta
            )

            # Não cria novamente uma partida já cadastrada.
            if partida_existente is not None:
                print(
                    f"{cenario['fase']} já existe. "
                    f"ID interno: {partida_existente.id}"
                )

                # Avança para o próximo cenário.
                continue

            # Calcula uma data futura diferente para cada partida.
            inicio_futuro = (
                datetime.now(timezone.utc)
                + timedelta(days=cenario["dias"])
            )

            # Cria o objeto ORM usando os dados do cenário.
            partida = Partida(
                external_id=cenario["external_id"],
                time_casa=cenario["time_casa"],
                time_visitante=cenario["time_visitante"],
                inicio_em=inicio_futuro,
                fase=cenario["fase"],
                status=StatusPartida.AGENDADA,
            )

            # Coloca a partida na fila de inserção.
            database.add(partida)

            # Envia o INSERT para obter o ID interno.
            database.flush()

            # Mostra o ID que será utilizado no Swagger.
            print(
                f"{cenario['fase']} criada. "
                f"ID interno: {partida.id}"
            )

        # Confirma conjuntamente todos os novos cenários.
        database.commit()

    # Captura qualquer falha durante a criação.
    except Exception:
        # Desfaz todas as inserções desta execução.
        database.rollback()

        # Reenvia o erro para mostrar o traceback.
        raise

    # Executa independentemente de sucesso ou erro.
    finally:
        # Fecha a sessão com o banco.
        database.close()


# Executa a função quando o script é chamado pelo terminal.
if __name__ == "__main__":
    # Cria os cenários definidos acima.
    criar_partidas_demo()