#validar_idade() - funcionou 
#validar_senha() - a principio ta funcionando tbm
#verificar_cpf()
#verificar_email()
#verificar_login()
#cadastrar_usuario()

from usuario import Usuario
from datetime import datetime

def validar_idade(data_nascimento): #Precisa ser maior de 18 anos

    try:  #Tenta executar um código que pode gerar erro
        # datetime.strptime transforma a data informada em um formato de data que o python entenda
        nascimento = datetime.strptime(
            data_nascimento,
            "%d/%m/%Y"
        )
    # usando o try antes, caso seja inserido um valor invalido, ele segue para o except sem quebrar o programa
    except ValueError: #dessa forma o 'except' espera especificamente um erro de valor inválido (Value Error)
        return False

    hoje = datetime.today()

    idade = hoje.year - nascimento.year

    if (
        (hoje.month, hoje.day)
        <
        (nascimento.month, nascimento.day)
    ):
        idade -= 1

    return idade >= 18

def validar_senha(senha): #8 caracteres, maiuscula, minuscula, numero e especial

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

