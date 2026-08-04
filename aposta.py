
class Aposta:
    def __init__(
            self,
            id_aposta,
            usuario,
            partida,
            gols_home,
            gols_away,
            valor_apostado,
            odd=2.0,
            premio=0
    ):
        self.id_aposta = id_aposta
        self.usuario = usuario
        self.partida = partida

        self.gols_home = gols_home
        self.gols_away = gols_away

        self.valor_apostado = valor_apostado
        self.odd = odd
        self.premio = premio

    def __str__(self):
        return (
            f"Aposta: {self.id_aposta}\n"
            f"Usuário: {self.usuario.nome}\n"
            f"Partida ID: {self.partida.id_partida}\n"
            f"Partida: {self.partida.home_team} x {self.partida.away_team}\n"
            f"Palpite: {self.gols_home} x {self.gols_away}\n"
            f"Valor apostado: {self.valor_apostado}\n"
            f"Odd: {self.odd}\n"
            f"Prêmio: {self.premio}"
        )