#validar_idade()
#validar_senha()
#cadastrar_usuario()

def validar_idade(data_nascimento):
    pass


def validar_senha(senha):
    pass


def verificar_cpf(cpf, usuarios):

    for usuario in usuarios:

        if usuario.cpf == cpf:
            return True

    return False


def cadastrar_usuario():
    pass