#CAMADA DE APRESENTAÇÃO

from usuario import Usuario
from usuario_service import (
    cadastrar_usuario,
    autenticar_usuario,
    consultar_saldo,
    trocar_senha,
    cancelar_participacao
)
from partida_service import (
    criar_partida,
    listar_partidas,
    atualizar_resultado
)
from api_service import carregar_partidas_api

#TESTE PROVISÓRIO-------------------------------


#---------------------------------------------------

usuarios = [] #lista para guardar os usuários cadastrados
usuario_logado = None
partidas = [] #lista para guardar as partidas

#-- MENU GERAL ------------------------------
while True:
    print("\n===== SISTEMA DE APOSTAS =====")
    print("1 - Cadastrar usuário")
    print("2 - Login")
    print("3 - Administrador")
    print("4 - Sair")

    opcao = input("Escolha uma opção: ")
#-- OPÇÃO 1 MENU GERAL ------------------------------
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

#-- OPÇÃO 2 MENU GERAL ---------------------------------
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

    #ÁREA DO USUÁRIO JA LOGADO
        #MENU USUÁRIO
            while usuario_logado is not None:
                print("\n===== ÁREA DO USUÁRIO =====")
                print("1 - Consultar saldo")
                print("2 - Trocar senha")
                print("3 - Cancelar participação")
                print("4 - Logout")
            
                opcao_usuario = input(
                    "Escolha uma opção: "
                )
                if opcao_usuario == "1": #CONSULTA SALDO
                    saldo = consultar_saldo(usuario_logado)
                    print(
                        f"Saldo atual: "
                        f"{saldo} pontos"
                    )

                elif opcao_usuario == "2":  #TROCAR SENHA
                    senha_atual = input("Senha atual: ")
                    nova_senha = input("Nova senha: ")
                    sucesso, mensagem = trocar_senha(
                        usuario_logado, senha_atual, nova_senha
                    )
                    print(mensagem)

                elif opcao_usuario == "3":  #CANCELAR PARTICIPAÇÃO
                    confirmar = input(
                        "Tem certeza que deseja cancelar sua participação? (S/N): "
                    ).upper()
                    if confirmar == "S":
                        sucesso, mensagem = cancelar_participacao(
                            usuario_logado
                        )
                        print(mensagem)
                        usuario_logado = None
                    else:
                        print("Operação cancelada.")


                elif opcao_usuario == "4":  #LOGOUT
                    usuario_logado = None
                    print("Logout realizado.")

                else:
                    print("Opção inválida.")



#-- OPÇÃO 3 MENU GERAL ---------------------------------
    elif opcao == "3":
        while True:
            print("\n=== MENU DO ADMINISTRADOR ===")

            print("1 - Cadastrar partida")
            print("2 - Listar partidas")
            print("3 - Atualizar resultado")
            print("4 - Voltar")

            opcao_admin = input("Escolha uma opção: ")
            if opcao_admin == "4":
                break


#-- OPÇÃO 4 MENU GERAL ---------------------------------
    elif opcao == "4":
        print("Encerrando sistema.")
        break


    else:
        print("Opção inválida.")
