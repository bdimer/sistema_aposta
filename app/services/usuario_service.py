
"""Implementa as regras de negócio relacionadas aos usuários."""

from datetime import date
import re
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.usuario import Usuario
from app.repositories.usuario_repository import(
    adicionar_usuario,
    atualizar_usuario,
    buscar_usuario_por_cpf,
    buscar_usuario_por_email,
    buscar_usuario_por_login,
    listar_usuarios_ranking,
)
from app.schemas.usuario import (
    TrocaSenha,
    UsuarioCreate,
    UsuarioLogin,
    RankingUsuarioResponse,
)
from app.services.security import (
    gerar_hash_senha,
    verificar_senha,
)


# cria uma exceção específica para violação de regras do sistema
class ErroRegraNegocio(ValueError):
    """Representa uma operação recusada por uma regra de negócio."""
# Cria uma exceção para falha inesperada de persistência
class ErroPersistencia(RuntimeError):
    """Representa uma falha ao ler ou gravar dados no banco."""

# Remove pontos, traços e espaços do CPF
def normalizar_cpf(cpf:str) -> str:
    """Devolve somente os números presentes no CPF."""

    # A expressão \D representa qualquer caractere que não seja número
    return re.sub(r"\D", "", cpf)


# Verifica se a data de nascimento representa uma pessoa adulta
def validar_maioridade(data_nascimento: date) -> bool:
    """Retorna True quando o usuário tem pelo menos 18 anos."""

    hoje = date.today()
    idade = hoje.year - data_nascimento.year

    aniversario_ainda_nao_ocorreu = (
        hoje.month,
        hoje.day,
    ) < (
        data_nascimento.month,
        data_nascimento.day,
    )
    if aniversario_ainda_nao_ocorreu:
        idade -= 1

    return idade >= 18


# Verifica os requisitos de segurança da senha
def validar_complexidade_senha(senha: str) -> bool:
    """Retorna True quando a senha atende a todos os requisitos."""

    tem_tamanho_minimo = len(senha) >= 8

    tem_maiuscula = any(
        caractere.isupper()
        for caractere in senha
    )

    tem_minuscula = any(
        caractere.islower()
        for caractere in senha
    )

    tem_numero = any(
        caractere.isdigit()
        for caractere in senha
    )

    tem_especial = any(
        not caractere.isalnum()
        and not caractere.isspace()
        for caractere in senha
    )

    return(
        tem_tamanho_minimo
        and tem_maiuscula
        and tem_minuscula
        and tem_numero
        and tem_especial
    )


# Cadastra usuario depois de executar todas as validações
def cadastrar_usuario(
        database: Session,
        dados: UsuarioCreate,
) -> Usuario:
    """Valida, protege e persiste um novo usuário."""

    nome_normalizado = dados.nome.strip() #Remove espaços extras inicio e fim do nome

    email_normalizado = str(dados.email).strip().lower() #converte para minusculo

    login_normalizado = dados.login.strip().lower()

    cpf_normalizado = normalizar_cpf(dados.cpf) #remove pontuação antes de armazenar

    if len(cpf_normalizado) != 11:
        raise ErroRegraNegocio(
            "O CPF deve possuir exatamente 11 números."
        )

    # Aplica regra para permitir somente usuários adultos
    if not validar_maioridade(dados.data_nascimento):
        raise ErroRegraNegocio(
            "O usuário deve possuir pelo menos 18 anos."
        )

    #Aplica requisitos segurança da senha
    if not validar_complexidade_senha(dados.senha):
        raise ErroRegraNegocio(
            "A senha deve possuir pelo menos 8 caracteres, "
            "uma letra maiúscula, uma letra minúscula, "
            "um número e um caractere especial."
        )

    # consulta banco para impedir CPF duplicado
    if buscar_usuario_por_cpf(database, cpf_normalizado):
        raise ErroRegraNegocio(
            "CPF já cadastrado."
        )

    # consulta banco para impedir email duplicado
    if buscar_usuario_por_email(database, email_normalizado):
        raise ErroRegraNegocio(
            "E-mail já cadastrado."
        )

    # Impede login duplicado
    if buscar_usuario_por_login(database, login_normalizado):
        raise ErroRegraNegocio(
            "Login já cadastrado."
        )

    # Cria objeto ORM que representa a nova linha na tabela
    novo_usuario = Usuario(
        nome=nome_normalizado,
        email=email_normalizado,
        cpf=cpf_normalizado,
        data_nascimento=dados.data_nascimento,
        login=login_normalizado,
        senha_hash=gerar_hash_senha(dados.senha),
    )

    # Inicia tratamento de operações que altera o banco
    try:
        adicionar_usuario(database, novo_usuario)

        database.commit()

        database.refresh(novo_usuario)

        return novo_usuario


    #Pode ocorrer se outra requisição cadastrar o mesmo dado simultaneamente
    except IntegrityError as erro:

        database.rollback() # desfaz transação que apresentou conflito

        raise ErroRegraNegocio(
            "CPF, e-mail ou login já cadastrado."
        ) from erro 

    # Captura outras falhas relacionadas ao banco
    except SQLAlchemyError as erro:

        database.rollback()

        raise ErroPersistencia(
            "Não foi possivel cadastrar o usuário."
        ) from erro 

# Verifica credenciais enviadas no login
def autenticar_usuario(
        database: Session,
        dados: UsuarioLogin,
) -> Usuario:
    """Retorna o usuario quando o login e a senha são válidos."""

    login_normalizado = dados.login.strip().lower()

    usuario = buscar_usuario_por_login(
        database,
        login_normalizado,
    )
    if usuario is None:
        raise ErroRegraNegocio(
            "Login ou senha inválidos."
        )
    if not usuario.ativo:
        raise ErroRegraNegocio(
            "Usuário inativo."
        )
    if not verificar_senha(
        dados.senha,
        usuario.senha_hash,
    ):
        raise ErroRegraNegocio(
            "Login ou senha inválidos."
        )
    return usuario


#Altera senha de conta ja autenticada
def trocar_senha(
        database: Session,
        usuario: Usuario,
        dados: TrocaSenha,
) -> Usuario:
    """Confere a senha atual e armazena o hash da nova senha."""

    if not verificar_senha(
        dados.senha_atual,
        usuario.senha_hash,
    ):
        raise ErroRegraNegocio(
            "Senha atual incorreta."
        )

    if not validar_complexidade_senha(dados.nova_senha):
        raise ErroRegraNegocio(
            "A nova senha não atende aos requisitos de segurança."
        )

    if verificar_senha(  #Impede nova senha de ser igual a atual
        dados.nova_senha,
        usuario.senha_hash,
    ):
        raise ErroRegraNegocio(
            "A nova senha deve ser diferente da senha atual."
        )
    #Atualiza hash da senha nova
    usuario.senha_hash = gerar_hash_senha(
        dados.nova_senha
    )

    try:
        atualizar_usuario(database, usuario)
        database.commit()
        database.refresh(usuario)
        return usuario


    except SQLAlchemyError as erro:
        database.rollback()
        raise ErroPersistencia(
            "Não foi possivel alterar a senha."
        ) from erro


# Inativa conta sem excluir dados da conta
def inativar_usuario(
        database: Session,
        usuario: Usuario,
) -> Usuario:
    """Retira o acesso da conta, preservando seu histórico e saldo."""

    if not usuario.ativo: # Impede repetição desnecessária da operação
        raise ErroRegraNegocio(
            "O usuário ja está inativo."
        )
    usuario.ativo = False

    try:
        atualizar_usuario(database, usuario)
        database.commit()
        database.refresh(usuario)
        return usuario

    except SQLAlchemyError as erro:
        database.rollback()
        raise ErroPersistencia(
            "Não foi possivel inativar o usuário."
        ) from erro


#------
# Monta o ranking público usando o saldo dos usuários.
def consultar_ranking(
    database: Session,
) -> list[RankingUsuarioResponse]:
    """Retorna usuários ativos e inativos ordenados pelo saldo."""

    usuarios = listar_usuarios_ranking(
        database
    )
    ranking: list[RankingUsuarioResponse] = []

    # Enumera os usuários começando a posição em um.
    for posicao, usuario in enumerate(
        usuarios,
        start=1,
    ):
        # Cria uma entrada sem dados sensíveis.
        item_ranking = RankingUsuarioResponse(
            posicao=posicao,
            usuario_id=usuario.id,
            nome=usuario.nome,
            saldo=usuario.saldo,
            ativo=usuario.ativo,
        )
        ranking.append(item_ranking)

    # Devolve a classificação completa.
    return ranking