#CAMADA DE APRESENTAÇÃO

from usuario import Usuario
from usuario_service import (
    cadastrar_usuario,
    autenticar_usuario,
    consultar_saldo
)

usuarios = []
usuario_logado = None

while True:
    print("\n===== SISTEMA DE APOSTAS =====")
    print("1 - Cadastrar usuário")
    print("2 - Login")
    print("3 - Sair")

    opcao = input("Escolha uma opção: ")
#--------------------------------
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
            print("\n- Cadastro realizado com sucesso! -")
            print(resultado)
        else:
            print(resultado)

#-----------------------------------
    elif opcao == "2":
        login = input("Login: ")
        senha = input("Senha: ")

        sucesso, resultado = autenticar_usuario(
            login,
            senha,
            usuarios
        )

        if sucesso:
            usuario_logado = resultado
            print(f"Bem vindo, {usuario_logado.nome}!")

            while usuario_logado is not None:
                print("\n===== ÁREA DO USUÁRIO =====")
                print("1 - Consultar saldo")
                print("2 - Logout")
            
                opcao_usuario = input(
                    "Escolha uma opção: "
                )
                if opcao_usuario == "1":
                    saldo = consultar_saldo(usuario_logado)
                    print(
                        f"Saldo atual: "
                        f"{saldo} pontos"
                    )
                elif opcao_usuario == "2":
                    usuario_logado = None
                    print("Logout realizado.")

                else:
                    print("Opção inválida.")


#-----------------------------------
    elif opcao == "3":
        print("Encerrando sistema.")
        break


    else:
        print("Opção inválida.")
