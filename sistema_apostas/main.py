#CAMADA DE APRESENTAÇÃO

from usuario import Usuario
from usuario_service import cadastrar_usuario

usuarios = []

while True:
    print("\n===== SISTEMA DE APOSTAS =====")
    print("1 - Cadastrar usuário")
    print("2 - Sair")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        nome = input("Nome: ")
        email = input("Email: ")
        cpf = input("CPF: ")
        data_nascimento = input(
            "Data de nascimento (dd/mm/aaaa): "
        )
        login = input("Login: ")
        senha = input("Senha: ")

        sucesso, resultado = cadastrar_usuario(
            nome,
            email,
            cpf,
            data_nascimento,
            login,
            senha,
            usuarios
        )
        if sucesso:
            print("Cadastro realizado com sucesso!")
            print(resultado)
        else:
            print(resultado)


    elif opcao == "2":
        print("Encerrando sistema.")
        break


    else:
        print("Opção inválida.")