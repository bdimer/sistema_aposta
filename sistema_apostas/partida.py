


#- id_partida (identificador unico da partida)
#- home_team  (quem joga em casa, time A)
#- away_team (quem joga fora, time B)
#- data (data da partida)
#- hora (horario da partida)
#- fase (grupos, oitavas, quartas, semifinal, final)
#- status (agendada, em andamento, encerrada)
#placar_casa
#placar_visitante
#odd_home (casa, time A)
#odd_draw (empate)
#odd_away (visitante, time B)

class Partida:
    def __init__(
        self,
        id_partida,
        home_team,
        away_team,
        data,
        hora,
        fase,
        odd_home,
        odd_draw,
        odd_away
    ):
        self.id_partida = id_partida
        self.home_team = home_team
        self.away_team = away_team 
        self.data = data 
        self.hora = hora 
        self.fase = fase 
        self.odd_home = odd_home
        self.odd_draw = odd_draw
        self.odd_away = odd_away
        self.home_score = None
        self.away_score = None
        self.status = "AGENDADA"
    

    def __str__(self): #transforma o objeto em texto facil de ler
        return(
            f"ID: {self.id_partida}\n"
            f"Partida: {self.home_team}\n"
            f"Data: {self.data} as {self.hora}\n"
            f"Fase: {self.fase}\n"
            f"Status: {self.status}"
        )