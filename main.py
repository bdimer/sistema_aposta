#CAMADA DE APRESENTAÇÃO

#-- IMPORTAÇÕES ----------------------------
from usuario import Usuario

from usuario_service import (
    cadastrar_usuario,
    autenticar_usuario,
    consultar_saldo,
    trocar_senha,
    cancelar_participacao,
    buscar_usuario_por_login
)

from partida_service import (
    criar_partida,
    listar_partidas,
    buscar_partida_por_id,
    atualizar_resultado
)

from api_service import carregar_partidas_api

from aposta_service import (
    criar_aposta,
    listar_aposta,
    buscar_aposta
)


#-- DADOS DO SISTEMA -----------------------
usuarios = [] #lista para guardar os usuários cadastrados
usuario_logado = None

partidas = carregar_partidas_api()
apostas = []

#---------

def menu_fazer_aposta(usuario, partidas, apostas):
    print("\n==== FAZER APOSTA ====")

    print(listar_partidas(partidas))

    try:
        id_partida = int(input("Digite o ID da partida: "))
    except ValueError:
        print("O ID da partida deve ser um número.")
        return

    partida = buscar_partida_por_id(id_partida, partidas)

    if partida is None:
        print("Partida não encontrada.")
        return

    if partida.status != "SCHEDULED":
        print("Esta partida não está disponível para apostas.")
        return

    print(
        f"\nVocê escolheu: "
        f"{partida.home_team}x{partida.away_team}"
    )
    try:
        gols_home = int(
            input(f"Gols de {partida.home_team}: ")
        )
        gols_away = int(
        input(f"Gols de {partida.away_team}: ")

        )
        valor_apostado = float(
            input("Quantidade de pontos para apostar: ")
        )

    except ValueError:
        print("Digite apenas valores numéricos.")
        return

    sucesso, mensagem = criar_aposta(
        usuario,
        partida,
        gols_home,
        gols_away,
        valor_apostado,
        apostas
    )
    print(mensagem)

#-----------

def menu_cadastro_usuario(usuarios):
    while True:
        print("\n==== CADASTRO DE USUÁRIO ====")

        nome = input("Nome: ")
        email = input("E-mail: ")
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
            return

        print(f"\nErro: {resultado}")
        
        tentar_novamente = input(
            "Deseja tentar novamente? (S/N): "
        ).upper()
        if tentar_novamente != "S":
            return

#-----------

def menu_login_usuario(usuarios):
    while True:
        print("\n==== LOGIN ====")

        login = input("Login: ")
        usuario = buscar_usuario_por_login(login, usuarios)

        if usuario is None:
            print("Usuário não encontrado.")
            tentar_novamente = input("Deseja tentar novamente? (S/N): ").upper()
            if tentar_novamente != "S":
                return None
            continue

        if not usuario.status:
            print("Usuário inativo.")
            return None

        while True:
            senha = input("Senha: ")

            if usuario.senha == senha:
                print(f"Bem-vindo, {usuario.nome}!")
                return usuario

            print("Senha incorreta.")
            tentar_novamente = input("Deseja tentar novamente? (S/N): ").upper()
            if tentar_novamente != "S":
                return None
        

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
        menu_cadastro_usuario(usuarios)

#-- OPÇÃO 2 MENU GERAL ---------------------------------
    elif opcao == "2":
        usuario_logado = menu_login_usuario(usuarios)

    #-- ÁREA DO USUÁRIO JA LOGADO --------------------------
        #-- MENU USUÁRIO --
        if usuario_logado is not None:
            while usuario_logado is not None:
                print("\n===== ÁREA DO USUÁRIO =====")
                print("1 - Consultar saldo")
                print("2 - Listar partidas")
                print("3 - Fazer aposta") 
                print("4 - Minhas apostas") #-- falta
                print("5 - Ranking") #-- falta
                print("6 - Trocar senha")
                print("7 - Cancelar participação")
                print("8 - Logout")
            
                opcao_usuario = input("Escolha uma opção: ")
        #-- OPÇÃO 1 --
                if opcao_usuario == "1": #CONSULTA SALDO
                    saldo = consultar_saldo(usuario_logado)
                    print(f"Saldo atual: {saldo} pontos"
                    )

        #-- OPÇÃO 2 --
                elif opcao_usuario == "2":
                    print(listar_partidas(partidas))

        #-- OPÇÃO 3 --
                elif opcao_usuario == "3":
                    menu_fazer_aposta(usuario_logado, partidas, apostas)

        #-- OPÇÃO 4 --

        #-- OPÇÃO 5 --

        #-- OPÇÃO 6 --
                elif opcao_usuario == "6":  #TROCAR SENHA
                    senha_atual = input("Senha atual: ")
                    nova_senha = input("Nova senha: ")
                    sucesso, mensagem = trocar_senha(
                        usuario_logado, senha_atual, nova_senha
                    )
                    print(mensagem)

        #-- OPÇÃO 7 --
                elif opcao_usuario == "7":  #CANCELAR PARTICIPAÇÃO
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

        #-- OPÇÃO 8 --
                elif opcao_usuario == "8":  #LOGOUT
                    usuario_logado = None
                    print("Logout realizado.")

                else:
                    print("Opção inválida.")



#-- OPÇÃO 3 MENU GERAL ---------------------------------
    elif opcao == "3":
        while True:
            print("\n=== MENU DO ADMINISTRADOR ===")

            print("1 - Atualizar partidas pela API")
            print("2 - Listar partidas")
            print("3 - Atualizar resultado")
            print("4 - Encerrar apostas")
            print("5 - Calcular resultados")
            print("6 - Ranking")
            print("7 - Voltar")

            opcao_admin = input("Escolha uma opção: ")
            if opcao_admin == "7":
                break


#-- OPÇÃO 4 MENU GERAL ---------------------------------
    elif opcao == "4":
        print("Encerrando sistema.")
        break


    else:
        print("Opção inválida.")
