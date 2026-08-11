
from aposta import Aposta


#--------------------------------------------
def criar_aposta(
        usuario,
        partida,
        gols_home,
        gols_away,
        valor_apostado,
        apostas
):

    if usuario.status:
        return False, "Usuário inativo."

    if partida.status != "SCHEDULED": #uma partida FINISHED, IN_PLAY ou qualquer outro status não poderá receber novas apostas
        return False, "Esta partida não está disponível para apostas."

    if gols_home < 0 or gols_away < 0: #verifica se os gols são validos
        return False, "Os gols não podem ser negativos."

    if valor_apostado <= 0:
        return False, "O valor apostado deve ser maior que zero."

    if valor_apostado > usuario.saldo:
        return False, "Saldo insuficiente para realizar a aposta."

    id_aposta = len(apostas) + 1

    usuario.saldo -= valor_apostado #desconta os pontos apostados

    nova_aposta = Aposta(
        id_aposta,
        usuario,
        partida,
        gols_home,
        gols_away,
        valor_apostado
    )

    apostas.append(nova_aposta)

    return True, "Aposta registrada com sucesso!"

#-------------------------------------

def listar_aposta(apostas):
    if len(apostas) == 0:
        return "Nenhuma aposta cadastrada."

    resultado = ""

    for aposta in apostas:
        resultado += str(aposta)
        resultado += "\n-----------------\n"

    return resultado

#-------------------------------------

def buscar_aposta(id_aposta, apostas):
    for aposta in apostas:
        if aposta.id_aposta == id_aposta:
            return aposta

    return None