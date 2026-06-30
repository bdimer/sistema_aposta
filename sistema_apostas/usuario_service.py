#REGRAS DO NEGÓCIO

#validar_idade() - funcionou 
#validar_senha() - a principio ta funcionando tbm
#verificar_cpf() - OK
#verificar_email() - OK
#verificar_login() - OK
#cadastrar_usuario()

from usuario import Usuario
from datetime import datetime


#VALIDAR IDADE
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


#VALIDAR SENHA
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

#VERIFICAR CPF
def verificar_cpf(cpf, usuarios): #VALIDAR CPF

    for usuario in usuarios:

        if usuario.cpf == cpf:
            return True

    return False


#VERIFICAR E-MAIL
def verificar_email(email, usuarios):  #VALIDAR EMAIL

    for usuario in usuarios:

        if usuario.email == email:
            return True

    return False

#VERIFICAR LOGIN
def verificar_login(login, usuarios):  #VALIDAR LOGIN

    for usuario in usuarios:

        if usuario.login == login:
            return True

    return False

#CADASTRAR USUÁRIO
def cadastrar_usuario(    #CADASTRAR USUÁRIO
    nome,
    email,
    cpf,
    data_nascimento,
    login,
    senha,
    usuarios
):

    if not validar_idade(data_nascimento): # not inverte o resultado
        return False, "Usuário deve ter 18 anos ou mais."  # no caso se for false, not false retorna True, e entra no bloco

    if not validar_senha(senha):
        return False, (
            "A senha deve possuir "
            "8 caracteres, letra maiúscula, "
            "minúscula, número e caractere especial."
        )

    if verificar_cpf(cpf, usuarios):
        return False, "CPF já cadastrado."

    if verificar_email(email, usuarios):
        return False, "E-mail já cadastrado."

    if verificar_login(login, usuarios):
        return False, "Login já cadastrado."

    novo_usuario = Usuario(
        nome,
        email,
        cpf,
        data_nascimento,
        login,
        senha
    )

    usuarios.append(novo_usuario) # .append coloca usuario dentro da lista

    return True, novo_usuario

#AUTENTICAR USUÁRIO
def autenticar_usuario(
        login,
        senha,
        usuarios
):
    for usuario in usuarios:
        if usuario.login == login:
            if usuario.senha == senha:
                return True, usuario
            
            return False, "Senha incorreta."
        if not usuario.status:
            return False, "Usuário inativo."

    return False, "Usuário não encontrado."


#CONSULTAR SALDO USUARIO
def consultar_saldo(usuario):
    return usuario.pontos


#TROCAR SENHA
def trocar_senha(
        usuario, senha_atual, nova_senha
):
    if usuario.senha != senha_atual:
        return False, "Senha atual incorreta."
    
    if not validar_senha(nova_senha): #aproveita a função de validação ja existente
        return(
            False, "A nova senha não atende aos requisitos."
        )
    usuario.senha = nova_senha

    return True, "Senha alterada com sucesso."

#CANCELAR PARTICIPAÇÃO (FICAR INATIVO SEM APAGAR OS DADOS DO USUARIO)
def cancelar_participacao(usuario):
    usuario.status = False
    return True, "Participação cancelada com sucesso."
