#Apenas configurações do sistema, guarda informações que podem mudar
#Constantes

import os   # os permite acessar recursos do sistema operacional
from dotenv import load_dotenv  #importa a função que lê o .env

load_dotenv()

API_KEY = os.getenv("API_KEY")

BASE_URL = "https://api.football-data.org/v4"

ENDPOINT_MATCHES = "/competitions/WC/matches"

HEADERS = {
    "X-Auth-Token": API_KEY
}
