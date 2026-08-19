"""Testa a entrega dos arquivos básicos da interface visual."""


from fastapi.testclient import TestClient


# Confirma que a página principal é entregue pelo FastAPI.
def test_pagina_inicial_carrega(client: TestClient) -> None:
    """A página inicial deve conter os controles de acesso."""

    # Solicita a raiz da aplicação como um navegador faria.
    resposta = client.get("/")

    # Confirma que o arquivo HTML foi encontrado.
    assert resposta.status_code == 200

    # Confirma que o navegador receberá conteúdo HTML.
    assert resposta.headers["content-type"].startswith(
        "text/html"
    )

    # Verifica um texto essencial da tela de entrada.
    assert "Sistema de Apostas" in resposta.text

    # Verifica a existência da opção administrativa.
    assert "Entrar na área administrativa" in resposta.text

    # Confirma que o histórico de partidas pode ser acessado.
    assert "Encerradas" in resposta.text


# Confirma que os recursos referenciados pelo HTML estão disponíveis.
def test_arquivos_estaticos_carregam(
    client: TestClient,
) -> None:
    """CSS e JavaScript devem ser entregues sem erro HTTP."""

    # Solicita a folha responsável pelo estilo da página.
    resposta_css = client.get("/static/styles.css")

    # Solicita o código responsável pela comunicação com a API.
    resposta_javascript = client.get("/static/app.js")

    # Confirma que o arquivo CSS foi encontrado.
    assert resposta_css.status_code == 200

    # Confirma que o arquivo JavaScript foi encontrado.
    assert resposta_javascript.status_code == 200

    # Verifica se o CSS possui a variável principal de cor.
    assert "--green" in resposta_css.text

    # Verifica se o JavaScript possui a função central da API.
    assert "async function api" in resposta_javascript.text
