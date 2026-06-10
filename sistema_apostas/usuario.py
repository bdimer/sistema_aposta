class Usuario:

    def __init__(
        self,
        nome,
        email,
        cpf,
        data_nascimento,
        login,
        senha
    ):

        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        self.login = login
        self.senha = senha

        self.pontos = 100
        self.status = "ativo"