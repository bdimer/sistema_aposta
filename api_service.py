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
    print(url) #----------teste
    response = requests.get(
        url,
        headers=HEADERS
    )

    print(response.status_code) #-----teste
    print(response.text) #---------teste

    if response.status_code == 200:
        dados = response.json()
        return dados
    
    return None 