#Responsável apenas por conversar com a Football Data

import requests

from config import BASE_URL, HEADERS, ENDPOINT_MATCHES

def buscar_partidas_api():
    url = BASE_URL + ENDPOINT_MATCHES
    response = requests.get(
        url,
        headers=HEADERS
    )
    