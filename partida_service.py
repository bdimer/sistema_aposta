from partida import Partida


def criar_partida(
        id_partida,
        home_team,
        away_team,
        data,
        hora,
        fase,
        odd_home,
        odd_draw,
        odd_away,
        status,
        partidas
):
    nova_partida = Partida(
        id_partida,
        home_team,
        away_team,
        data,
        hora,
        fase,
        odd_home,
        odd_draw,
        odd_away,
        status
    )
    partidas.append(nova_partida)

    return True, "Partida cadastrada com sucesso."



def listar_partidas(partidas):
    if len(partidas) == 0:
        return "Nenhuma partida cadastrada."
    resultado = ""
    for partida in partidas:
        resultado += str(partida)
        resultado += "\n-----------------\n" #apenas separador para organizar melhor
    return resultado


def buscar_partida_por_id(id_partida, partidas):
    for partida in partidas:
        if partida.id_partida == id_partida:
            return partida
    return None


def atualizar_resultado(
        id_partida,
        home_score,
        away_score,
        partidas
):
    partida = buscar_partida_por_id(
        id_partida,
        partidas
    )
    if partida is None:
        return False, "Partida não encontrada."
    
    partida.home_score = home_score
    partida.away_score = away_score
    partida.status = "ENCERRADA" 
    return True, "Resultado atualizado com sucesso."



