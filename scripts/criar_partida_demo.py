"""Cria uma partida futura usada somente nos testes do projeto."""

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Partida, StatusPartida

# Reserva um identificador externo específico para a demonstração.
EXTERNAL_ID_DEMO = 999_999_999

# Cria a partida somente se ela ainda não existir.
def criar_partida_demo() -> None:
    """Insere uma partida agendada para permitir testes de apostas."""

    # Abre uma nova sessão com o banco.
    database = SessionLocal()

    try:
        consulta = select(Partida).where(
            Partida.external_id == EXTERNAL_ID_DEMO
        )
        partida_existente = database.scalar(
            consulta
        )
        # Encerra o script se a partida já estiver cadastrada.
        if partida_existente is not None:
            print(
                "A partida de demonstração já existe. "
                f"ID interno: {partida_existente.id}"
            )
            return

        # Calcula uma data sete dias depois do momento atual.
        inicio_futuro = (
            datetime.now(timezone.utc)
            + timedelta(days=7)
        )

        partida = Partida(
            external_id=EXTERNAL_ID_DEMO,
            time_casa="Brasil",
            time_visitante="Argentina",
            inicio_em=inicio_futuro,
            fase="DEMONSTRAÇÃO",
            status=StatusPartida.AGENDADA,
        )

        database.add(partida)
        database.commit()
        database.refresh(partida)

        print(
            "Partida de demonstração criada. "
            f"ID interno: {partida.id}"
        )

    except Exception:
        database.rollback()
        # Reenvia o erro para que o terminal mostre o traceback.
        raise
    # Este bloco sempre será executado.
    finally:
        database.close()

if __name__ == "__main__":
    criar_partida_demo()