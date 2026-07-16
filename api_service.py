#.GET - Buscar informações
#.POST - Enviar informações
#.PUT - Atualizar informações
#.DELETE - Remover informações

# api_service.py - Responsável apenas por conversar com a Football Data

import requests
print(requests.__version__)

from config import (
    BASE_URL,
    HEADERS,
    ENDPOINT_MATCHES
)


def buscar_partidas_api():
    url = BASE_URL + ENDPOINT_MATCHES
    response = requests.get(
        url,
        headers=HEADERS
    )
    if response.status_code == 200:
        pass