"""Concentra as operações da tabela de usuários no banco de dados."""


from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.usuario import Usuario 

# Procura usuario pela chave primaria
def buscar_usuario_por_id(
        database: Session,
        usuario_id: int,
) -> Usuario | None:
    """Retorna o usuário do ID informado ou None quando não existir."""

    consulta = select(Usuario).where(
        Usuario.id == usuario_id
    )
    return database.scalar(consulta)


# Procura conta pelo login
def buscar_usuario_por_login(
    database: Session,
    login: str,
) -> Usuario | None:
    """Retorna o usuario do login informado ou None."""

    consulta = select(Usuario).where(
        Usuario.login == login
    )
    return database.scalar(consulta)


# Verifica se o e-mail ja pertence a outra conta
def buscar_usuario_por_email(
        database: Session,
        email: str,
) -> Usuario | None:
    """Retorna o usuario encontrado pelo e-mail ou None."""

    consulta = select(Usuario).where(
        Usuario.email == email
    )
    return database.scalar(consulta)


# Verifica se o CPF ja foi cadastrado
def buscar_usuario_por_cpf(
        database: Session,
        cpf: str,
) -> Usuario | None:
    """Retorna o usuario encontrado pelo CPF ou None."""

    consulta = select(Usuario).where(
        Usuario.cpf == cpf
    )
    return database.scalar(consulta)


# Adiciona um novo usuario a transação atual
def adicionar_usuario(
        database: Session,
        usuario: Usuario,
) -> Usuario:
    """Adiciona o usuario a sessão sem confirmar a transação."""

    database.add(usuario)
    database.flush()
    database.refresh(usuario)

    return usuario


# Envia alterações de um usuario existente ao banco
def atualizar_usuario(
        database: Session,
        usuario: Usuario,
) -> Usuario:
    """Sincroniza as alterações do usuário dentro da transação atual."""

    database.add(usuario)
    database.flush()
    database.refresh(usuario)

    return usuario

#------
# Lista todos os usuários na ordem do ranking.
def listar_usuarios_ranking(
    database: Session,
) -> list[Usuario]:
    """Ordena usuários pelo saldo sem excluir contas inativas."""

    # Seleciona todos os usuários e organiza o maior saldo primeiro.
    consulta = select(Usuario).order_by(
        Usuario.saldo.desc(),
        # Usa o ID como desempate estável para saldos iguais.
        Usuario.id.asc(),
    )
    resultado = database.scalars(consulta).all()
    return list(resultado)



# Lista todos os usuários para operações administrativas.
def listar_todos_usuarios(
    database: Session,
) -> list[Usuario]:
    """Retorna usuários ativos e inativos em ordem de cadastro."""

    consulta = select(Usuario).order_by(
        Usuario.id.asc()
    )
    resultado = database.scalars(consulta).all()
    return list(resultado)