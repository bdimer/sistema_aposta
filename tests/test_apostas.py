"""Testa apostas, ODDs, multiplicação, liquidação e falência."""


from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import (
    Partida,
    StatusPartida,
)
from app.config import settings


# Cadastra um usuário e devolve seu cabeçalho de autenticação.
def criar_usuario_autenticado(
    client: TestClient,
) -> dict[str, str]:
    """Cria uma conta válida e devolve seu token Bearer."""

    cadastro = client.post(
        "/usuarios",
        json={
            "nome": "Apostador de Teste",
            "email": "apostador@example.com",
            "cpf": "123.456.789-00",
            "data_nascimento": "2000-05-20",
            "login": "apostador",
            "senha": "Aposta@123",
        },
    )
    # Confirma que o cadastro funcionou.
    assert cadastro.status_code == 201

    login = client.post(
        "/usuarios/login",
        data={
            "username": "apostador",
            "password": "Aposta@123",
        },
    )

    assert login.status_code == 200
    token = login.json()["access_token"]
    return {
        "Authorization": f"Bearer {token}",
        "X-Admin-Key": settings.admin_key,
    }


# Cria uma partida agendada no banco temporário.
def criar_partida_agendada(
    database: Session,
    external_id: int = 1000,
) -> Partida:
    """Cria e devolve uma partida disponível para apostas."""

    inicio = (
        datetime.now(timezone.utc)
        + timedelta(days=1)
    )

    partida = Partida(
        external_id=external_id,
        time_casa="Brasil",
        time_visitante="Argentina",
        inicio_em=inicio,
        fase="TESTE",
        status=StatusPartida.AGENDADA,
    )

    database.add(partida)
    database.commit()
    database.refresh(partida)
    return partida


# Testa débito, multiplicação e fórmula das ODDs.
def test_odds_e_multiplicacao(
    client: TestClient,
    database: Session,
) -> None:
    """Confirma ODD fixa, recálculo e débito adicional."""

    headers = criar_usuario_autenticado(client)
    partida = criar_partida_agendada(database)
    primeira = client.post(
        "/apostas",
        headers=headers,
        json={
            "partida_id": partida.id,
            "gols_casa": 2,
            "gols_visitante": 1,
            "valor_apostado": "10.00",
        },
    )
    assert primeira.status_code == 201

    primeira_id = primeira.json()["id"]
    assert primeira.json()["odd_registrada"] == "2.0000"

    # Multiplica a primeira aposta por três.
    multiplicacao = client.patch(
        f"/apostas/{primeira_id}/multiplicar",
        headers=headers,
        json={
            "multiplicador": 3,
        },
    )

#confirmações
    assert multiplicacao.status_code == 200
    assert multiplicacao.json()["multiplicador"] == 3
    assert multiplicacao.json()["valor_total"] == "30.00"
    assert multiplicacao.json()["odd_registrada"] == "2.0000"

    # Registra uma aposta no visitante.
    visitante = client.post(
        "/apostas",
        headers=headers,
        json={
            "partida_id": partida.id,
            "gols_casa": 0,
            "gols_visitante": 2,
            "valor_apostado": "10.00",
        },
    )

    assert visitante.json()["selecao"] == "AWAY"

    segunda_casa = client.post(
        "/apostas",
        headers=headers,
        json={
            "partida_id": partida.id,
            "gols_casa": 3,
            "gols_visitante": 1,
            "valor_apostado": "10.00",
        },
    )

    assert segunda_casa.json()["odd_registrada"] == "2.0000"

    consulta_partida = client.get(
        f"/partidas/{partida.id}",
        headers=headers,
    )

    assert consulta_partida.json()["odd_casa"] == "1.5000"
    assert consulta_partida.json()["odd_visitante"] == "3.0000"

    # Consulta o saldo depois de 50 pontos comprometidos.
    saldo = client.get(
        "/usuarios/me/saldo",
        headers=headers,
    )

    assert saldo.json()["saldo"] == "50.00"


# Testa pagamento de uma aposta e perda de outra.
def test_vitoria_e_derrota(
    client: TestClient,
    database: Session,
) -> None:
    """Confirma prêmio por placar exato e perda sem segundo débito."""

    headers = criar_usuario_autenticado(client)
    partida = criar_partida_agendada(
        database,
        external_id=1001,
    )

    client.post(
        "/apostas",
        headers=headers,
        json={
            "partida_id": partida.id,
            "gols_casa": 2,
            "gols_visitante": 1,
            "valor_apostado": "20.00",
        },
    )

    # Registra outra aposta que será perdedora.
    client.post(
        "/apostas",
        headers=headers,
        json={
            "partida_id": partida.id,
            "gols_casa": 0,
            "gols_visitante": 1,
            "valor_apostado": "10.00",
        },
    )

    # Liquida a partida com o placar exato da primeira aposta.
    liquidacao = client.patch(
        f"/partidas/{partida.id}/resultado",
        headers=headers,
        json={
            "gols_casa": 2,
            "gols_visitante": 1,
        },
    )

    assert liquidacao.status_code == 200
    assert liquidacao.json()["apostas_vencedoras"] == 1
    assert liquidacao.json()["apostas_perdedoras"] == 1
    assert liquidacao.json()["total_creditado"] == "40.00"

    # Consulta o saldo final.
    saldo = client.get(
        "/usuarios/me/saldo",
        headers=headers,
    )

    assert saldo.json()["saldo"] == "110.00"

    # Tenta liquidar novamente a mesma partida.
    repeticao = client.patch(
        f"/partidas/{partida.id}/resultado",
        headers=headers,
        json={
            "gols_casa": 2,
            "gols_visitante": 1,
        },
    )

    assert repeticao.status_code == 400


# Testa a devolução integral em um empate.
def test_empate_devolve_todas_as_apostas(
    client: TestClient,
    database: Session,
) -> None:
    """Confirma que empate real restaura todos os pontos apostados."""

    headers = criar_usuario_autenticado(client)

    partida = criar_partida_agendada(
        database,
        external_id=1002,
    )

    # Registra uma aposta de 20 pontos.
    client.post(
        "/apostas",
        headers=headers,
        json={
            "partida_id": partida.id,
            "gols_casa": 2,
            "gols_visitante": 1,
            "valor_apostado": "20.00",
        },
    )

    # Registra outra aposta de 10 pontos.
    client.post(
        "/apostas",
        headers=headers,
        json={
            "partida_id": partida.id,
            "gols_casa": 0,
            "gols_visitante": 2,
            "valor_apostado": "10.00",
        },
    )

    # Informa um empate como resultado real.
    liquidacao = client.patch(
        f"/partidas/{partida.id}/resultado",
        headers=headers,
        json={
            "gols_casa": 1,
            "gols_visitante": 1,
        },
    )

    assert liquidacao.json()["apostas_devolvidas"] == 2
    assert liquidacao.json()["apostas_vencedoras"] == 0
    assert liquidacao.json()["total_creditado"] == "30.00"

    # Consulta o saldo restaurado.
    saldo = client.get(
        "/usuarios/me/saldo",
        headers=headers,
    )

    assert saldo.json()["saldo"] == "100.00"


# Testa a falência somente depois da liquidação.
def test_falencia_apos_derrota(
    client: TestClient,
    database: Session,
) -> None:
    """Confirma saldo zero ativo enquanto pendente e inativo após perder."""

    # Cria e autentica o usuário.
    headers = criar_usuario_autenticado(client)

    # Cria a partida do cenário de falência.
    partida = criar_partida_agendada(
        database,
        external_id=1003,
    )

    # Aposta todos os 100 pontos em um placar.
    aposta = client.post(
        "/apostas",
        headers=headers,
        json={
            "partida_id": partida.id,
            "gols_casa": 1,
            "gols_visitante": 0,
            "valor_apostado": "100.00",
        },
    )

    assert aposta.status_code == 201

    # Confirma que a conta ainda acessa o perfil enquanto aguarda resultado.
    perfil_pendente = client.get(
        "/usuarios/me",
        headers=headers,
    )

    # Saldo zero com aposta pendente não representa falência definitiva.
    assert perfil_pendente.status_code == 200
    assert perfil_pendente.json()["saldo"] == "0.00"
    assert perfil_pendente.json()["ativo"] is True

    # Liquida a partida com o resultado oposto.
    liquidacao = client.patch(
        f"/partidas/{partida.id}/resultado",
        headers=headers,
        json={
            "gols_casa": 0,
            "gols_visitante": 1,
        },
    )

    assert liquidacao.json()["apostas_perdedoras"] == 1
    assert liquidacao.json()["usuarios_inativados"] == 1

    # Tenta reutilizar o token depois da falência.
    perfil_final = client.get(
        "/usuarios/me",
        headers=headers,
    )

    # Confirma que a conta perdeu o acesso.
    assert perfil_final.status_code == 403


    #--------------
    # Testa o bloqueio de uma operação sem chave administrativa.
def test_resultado_exige_chave_administrativa(
    client: TestClient,
    database: Session,
) -> None:
    """Confirma que usuário comum não pode informar resultados."""

    # Cria um usuário e recebe os cabeçalhos válidos.
    headers = criar_usuario_autenticado(client)

    # Remove a chave administrativa, mantendo somente o JWT.
    headers_sem_admin = headers.copy()
    headers_sem_admin.pop("X-Admin-Key")

    # Cria uma partida para a tentativa de liquidação.
    partida = criar_partida_agendada(
        database,
        external_id=1004,
    )

    # Tenta informar um resultado sem permissão administrativa.
    response = client.patch(
        f"/partidas/{partida.id}/resultado",
        headers=headers_sem_admin,
        json={
            "gols_casa": 1,
            "gols_visitante": 0,
        },
    )
    # Confirma que a operação foi bloqueada.
    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Chave administrativa não informada."
    )


#-------------
# Testa as operações administrativas exigidas na apresentação.
def test_admin_cria_e_pesquisa_aposta_e_usuario(
    client: TestClient,
    database: Session,
) -> None:
    """Confirma criação e pesquisa administrativa de dados."""

    # Cria um usuário e obtém JWT com chave administrativa.
    headers = criar_usuario_autenticado(client)

    # Consulta o perfil para descobrir o ID interno.
    perfil = client.get(
        "/usuarios/me",
        headers=headers,
    )

    # Obtém o identificador do usuário cadastrado.
    usuario_id = perfil.json()["id"]

    # Cria uma partida disponível para a aposta.
    partida = criar_partida_agendada(
        database,
        external_id=1005,
    )

    # O administrador cria uma aposta para o usuário.
    criacao = client.post(
        "/admin/apostas",
        headers=headers,
        json={
            "usuario_id": usuario_id,
            "partida_id": partida.id,
            "gols_casa": 2,
            "gols_visitante": 1,
            "valor_apostado": "10.00",
        },
    )

    # Confirma que a aposta foi criada.
    assert criacao.status_code == 201

    # Obtém o ID da aposta criada.
    aposta_id = criacao.json()["id"]

    # O administrador pesquisa a aposta pelo ID.
    pesquisa_aposta = client.get(
        f"/admin/apostas/{aposta_id}",
        headers=headers,
    )

    # Confirma que a aposta foi encontrada.
    assert pesquisa_aposta.status_code == 200

    # Confirma o proprietário da aposta.
    assert pesquisa_aposta.json()["usuario_id"] == usuario_id

    # O administrador solicita todos os usuários.
    usuarios = client.get(
        "/admin/usuarios",
        headers=headers,
    )

    # Confirma que a listagem funcionou.
    assert usuarios.status_code == 200

    # Confirma que existe um usuário na lista.
    assert len(usuarios.json()) == 1

    # O administrador pesquisa o usuário específico.
    pesquisa_usuario = client.get(
        f"/admin/usuarios/{usuario_id}",
        headers=headers,
    )

    # Confirma que o usuário foi encontrado.
    assert pesquisa_usuario.status_code == 200

    # Confirma que a senha não foi exposta.
    assert "senha_hash" not in pesquisa_usuario.json()


# Testa que a listagem ativa exclui apostas já liquidadas.
def test_listar_somente_apostas_ativas(
    client: TestClient,
    database: Session,
) -> None:
    """Confirma que /minhas/ativas devolve somente PENDING."""

    # Cria um usuário autenticado.
    headers = criar_usuario_autenticado(client)

    # Cria uma partida que continuará pendente.
    partida_pendente = criar_partida_agendada(
        database,
        external_id=1006,
    )

    # Cria outra partida que será encerrada.
    partida_encerrada = criar_partida_agendada(
        database,
        external_id=1007,
    )

    # Registra uma aposta que permanecerá ativa.
    aposta_pendente = client.post(
        "/apostas",
        headers=headers,
        json={
            "partida_id": partida_pendente.id,
            "gols_casa": 1,
            "gols_visitante": 0,
            "valor_apostado": "10.00",
        },
    )

    # Registra outra aposta para ser liquidada.
    client.post(
        "/apostas",
        headers=headers,
        json={
            "partida_id": partida_encerrada.id,
            "gols_casa": 2,
            "gols_visitante": 0,
            "valor_apostado": "10.00",
        },
    )

    # Encerra a segunda partida.
    liquidacao = client.patch(
        f"/partidas/{partida_encerrada.id}/resultado",
        headers=headers,
        json={
            "gols_casa": 2,
            "gols_visitante": 0,
        },
    )

    assert liquidacao.status_code == 200

    ativas = client.get(
        "/apostas/minhas/ativas",
        headers=headers,
    )

    assert ativas.status_code == 200

    assert len(ativas.json()) == 1

    assert ativas.json()[0]["id"] == aposta_pendente.json()["id"]

    assert ativas.json()[0]["status"] == "PENDING"