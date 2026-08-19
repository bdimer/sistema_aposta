"""Testa cadastro, validações, autenticação e inativação."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.usuario import Usuario


# Centraliza os dados válidos usados nos testes.
def dados_usuario_valido() -> dict:
    """Retorna um cadastro válido que pode ser alterado por cada teste."""

    # Devolve um novo dicionário em cada chamada.
    return {
        "nome": "Usuário de Teste",
        "email": "teste@example.com",
        "cpf": "123.456.789-00",
        "data_nascimento": "2000-05-20",
        "login": "usuario_teste",
        "senha": "Senha@123",
    }


# Verifica cadastro, saldo e proteção da senha.
def test_cadastrar_usuario_com_saldo_inicial(
    client: TestClient,
    database: Session,
) -> None:
    """Confirma cadastro válido com 100 pontos e hash Argon2."""

    # Envia uma requisição de cadastro para a API.
    response = client.post(
        "/usuarios",
        json=dados_usuario_valido(),
    )

    # Confirma que o recurso foi criado.
    assert response.status_code == 201

    # Converte o JSON recebido para dicionário.
    resposta = response.json()

    # Verifica o saldo inicial obrigatório.
    assert resposta["saldo"] == "100.00"

    # Verifica que a conta começa ativa.
    assert resposta["ativo"] is True

    # Confirma que a senha original não aparece.
    assert "senha" not in resposta

    # Confirma que o hash também não aparece.
    assert "senha_hash" not in resposta

    # Consulta o usuário diretamente no banco temporário.
    consulta = select(Usuario).where(
        Usuario.login == "usuario_teste"
    )

    # Executa a consulta.
    usuario = database.scalar(consulta)

    # Confirma que o usuário realmente foi persistido.
    assert usuario is not None

    # Confirma que a senha original não foi armazenada.
    assert usuario.senha_hash != "Senha@123"

    # Confirma que o algoritmo Argon2 foi utilizado.
    assert usuario.senha_hash.startswith("$argon2")


# Verifica a regra obrigatória de maioridade.
def test_recusar_usuario_menor_de_idade(
    client: TestClient,
) -> None:
    """Confirma que menores de 18 anos não podem se cadastrar."""

    # Obtém um cadastro inicialmente válido.
    dados = dados_usuario_valido()
    # Troca a data por uma que representa um menor.
    dados["data_nascimento"] = "2015-01-01"
    # Tenta cadastrar o usuário menor.
    response = client.post(
        "/usuarios",
        json=dados,
    )
    # Confirma que a regra recusou o cadastro.
    assert response.status_code == 400
    # Confirma que a mensagem explica o motivo.
    assert "18 anos" in response.json()["detail"]


# Verifica senha sem os requisitos obrigatórios.
def test_recusar_senha_fraca(
    client: TestClient,
) -> None:
    """Confirma que uma senha insegura é rejeitada."""

    # Obtém os dados válidos do cadastro.
    dados = dados_usuario_valido()
    # Substitui a senha por uma sem complexidade.
    dados["senha"] = "senhafraca"
    # Tenta cadastrar usando a senha inválida.
    response = client.post(
        "/usuarios",
        json=dados,
    )

    # Confirma a recusa da regra de negócio.
    assert response.status_code == 400

    # Confirma que a resposta menciona a senha.
    assert "senha" in response.json()["detail"].lower()


# Verifica que o mesmo CPF não pode ser cadastrado duas vezes.
def test_recusar_cpf_duplicado(
    client: TestClient,
) -> None:
    """Confirma a unicidade do CPF no serviço e no banco."""

    # Cadastra o primeiro usuário.
    primeira_resposta = client.post(
        "/usuarios",
        json=dados_usuario_valido(),
    )

    # Confirma que o primeiro cadastro funcionou.
    assert primeira_resposta.status_code == 201

    # Obtém uma nova cópia dos dados.
    segundo_usuario = dados_usuario_valido()

    # Altera e-mail para não gerar conflito nessa coluna.
    segundo_usuario["email"] = "outro@example.com"

    # Altera login para não gerar conflito nessa coluna.
    segundo_usuario["login"] = "outro_usuario"

    # Mantém o mesmo CPF e tenta cadastrar novamente.
    segunda_resposta = client.post(
        "/usuarios",
        json=segundo_usuario,
    )

    # Confirma que o CPF duplicado foi recusado.
    assert segunda_resposta.status_code == 400
    # Confirma que a mensagem identifica o conflito.
    assert "CPF já cadastrado" in segunda_resposta.json()["detail"]


# Verifica login, token e acesso a uma rota protegida.
def test_login_e_consulta_de_saldo(
    client: TestClient,
) -> None:
    """Confirma autenticação JWT e consulta do saldo inicial."""

    cadastro = client.post(
        "/usuarios",
        json=dados_usuario_valido(),
    )

    assert cadastro.status_code == 201

    login = client.post(
        "/usuarios/login",
        data={
            "username": "usuario_teste",
            "password": "Senha@123",
        },
    )

    # Confirma credenciais aceitas.
    assert login.status_code == 200

    # Extrai o token JWT da resposta.
    token = login.json()["access_token"]

    # Monta o cabeçalho usado nas rotas protegidas.
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # Consulta o saldo utilizando o token.
    saldo = client.get(
        "/usuarios/me/saldo",
        headers=headers,
    )

    # Confirma que a rota protegida foi acessada.
    assert saldo.status_code == 200

    # Confirma o saldo inicial.
    assert saldo.json()["saldo"] == "100.00"


# Verifica que a inativação bloqueia tokens e novos logins.
def test_inativar_usuario_bloqueia_acesso(
    client: TestClient,
) -> None:
    """Confirma que uma conta inativa perde o acesso ao sistema."""

    # Cadastra a conta usada neste teste.
    client.post(
        "/usuarios",
        json=dados_usuario_valido(),
    )

    # Autentica a conta.
    login = client.post(
        "/usuarios/login",
        data={
            "username": "usuario_teste",
            "password": "Senha@123",
        },
    )

    # Obtém o token válido.
    token = login.json()["access_token"]

    # Monta o cabeçalho Bearer.
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # Inativa a conta autenticada.
    inativacao = client.patch(
        "/usuarios/me/inativar",
        headers=headers,
    )

    # Confirma que a alteração foi realizada.
    assert inativacao.status_code == 200
    # Confirma o novo estado da conta.
    assert inativacao.json()["ativo"] is False

    # Tenta utilizar o token emitido antes da inativação.
    perfil = client.get(
        "/usuarios/me",
        headers=headers,
    )
    # Confirma que o token não dá mais acesso.
    assert perfil.status_code == 403

    # Tenta entrar novamente com a senha correta.
    novo_login = client.post(
        "/usuarios/login",
        data={
            "username": "usuario_teste",
            "password": "Senha@123",
        },
    )
    # Confirma que a conta inativa não pode autenticar.
    assert novo_login.status_code == 401