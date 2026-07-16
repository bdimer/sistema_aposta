#CAMADA DE DADOS

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

        # Valores definidos pelo sistema
        self.pontos = 100
        self.status = "ativo"
    
    #----------------------------------------
    def __str__(self):

        return (    # o f (formatted string) no inicio muda para str as variaveis
            f"Nome: {self.nome}\n" #\n faz quebra de linha 
            f"Email: {self.email}\n"
            f"CPF: {self.cpf}\n"
            f"Pontos: {self.pontos}\n"
            f"Status: {self.status}"
        )