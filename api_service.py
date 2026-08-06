#.GET - Buscar informações
#.POST - Enviar informações
#.PUT - Atualizar informações
#.DELETE - Remover informações

# api_service.py - Responsável apenas por conversar com a Football Data

import requests

from config import (
    BASE_URL,
    HEADERS,
    ENDPOINT_MATCHES
)

from partida import Partida

#------------------------------------------------
def buscar_partidas_api():
    url = BASE_URL + ENDPOINT_MATCHES
    
    response = requests.get(
        url,
        headers=HEADERS
    )

    if response.status_code == 200:
        dados = response.json()
        return dados
    
    return None 

#------------------------------------------------

def carregar_partidas_api():
    dados = buscar_partidas_api()

    if dados is None:
        return []
    
    partidas_api = dados["matches"]
    lista_partidas = []

    for partida_api in partidas_api:
        nova_partida = Partida(
            id_partida=partida_api["id"],
            home_team=partida_api["homeTeam"]["name"],
            away_team=partida_api["awayTeam"]["name"],
            status=partida_api["status"],
            data=partida_api["utcDate"][:10],
            hora=partida_api["utcDate"][11:16],
            fase=partida_api["stage"],
            odd_home=0,
            odd_draw=0,
            odd_away=0
        )

        lista_partidas.append(nova_partida)

    return lista_partidas