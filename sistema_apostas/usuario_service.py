#validar_idade()
#validar_senha()
#cadastrar_usuario()
from usuario import Usuario

def validar_idade(data_nascimento):
    pass

def validar_senha(senha):

    if len(senha) < 8:
        return False

    tem_maiuscula = False
    tem_minuscula = False
    tem_numero = False
    tem_especial = False

    for caractere in senha:

        if caractere.isupper():
            tem_maiuscula = True

        elif caractere.islower():
            tem_minuscula = True

        elif caractere.isdigit():
            tem_numero = True

        else:
            tem_especial = True

    return (
        tem_maiuscula and
        tem_minuscula and
        tem_numero and
        tem_especial
    )


def verificar_cpf(cpf, usuarios):

    for usuario in usuarios:

        if usuario.cpf == cpf:
            return True

    return False


def cadastrar_usuario():
    pass