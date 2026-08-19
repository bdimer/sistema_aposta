"""Concentra as operações da tabela de usuários no banco de dados."""

# Importa select para construir consultas SQL através do SQLAlchemy
from sqlalchemy import select

# Importa Session para representar uma sessão ativa com o banco
from sqlalchemy.orm import Session

# Importa modelo ORM correspondente a tabela de usuarios
from app.models.usuario import Usuario 

# Procura usuario pela chave primaria
def buscar_usuario_por_id(
        database: Session,
        usuario_id: int,
) -> Usuario | None:
    """Retorna o usuário do ID informado ou None quando não existir."""

    # Constroi um SELECT filtrando a coluna id
    consulta = select(Usuario).where(
        Usuario.id == usuario_id
    )

    # Executa a consulta e retorna um único usuario ou None
    return database.scalar(consulta)


# Procura conta pelo login
def buscar_usuario_por_login(
    database: Session,
    login: str,
) -> Usuario | None:
    """Retorna o usuario do login informado ou None."""

    # Constrói uma consulta que filtra a coluna login.
    consulta = select(Usuario).where(
        Usuario.login == login
    )
    #Executa a consulta dentro da sessão recebida
    return database.scalar(consulta)


# Verifica se o e-mail ja pertence a outra conta
def buscar_usuario_por_email(
        database: Session,
        email: str,
) -> Usuario | None:
    """Retorna o usuario encontrado pelo e-mail ou None."""

    #Monta a consulta usando a coluna de e-mail
    consulta = select(Usuario).where(
        Usuario.email == email
    )

    # Executa o SELECT e devolve resultado
    return database.scalar(consulta)


# Verifica se o CPF ja foi cadastrado
def buscar_usuario_por_cpf(
        database: Session,
        cpf: str,
) -> Usuario | None:
    """Retorna o usuario encontrado pelo CPF ou None."""

    # Monta a consulta usando a coluna de CPF
    consulta = select(Usuario).where(
        Usuario.cpf == cpf
    )

    # Executa o SELECT e devolve usuario encontrado
    return database.scalar(consulta)


# Adiciona um novo usuario a transação atual
def adicionar_usuario(
        database: Session,
        usuario: Usuario,
) -> Usuario:
    """Adiciona o usuario a sessão sem confirmar a transação."""

    # Coloca o objeto na fila de inserção do SQLAlchemy
    database.add(usuario)

    # Envia o INSERT ao banco sem finalizar definitivamente a transação
    database.flush()

    # Atualiza o objeto python com valores gerados pelo banco, como o ID
    database.refresh(usuario)

    # Devolve o mesmo usuario ja preenchido pelo banco
    return usuario


# Envia alterações de um usuario existente ao banco
def atualizar_usuario(
        database: Session,
        usuario: Usuario,
) -> Usuario:
    """Sincroniza as alterações do usuário dentro da transação atual."""

    # add também informa ao SQLAlchemy que o objeto deve ser acompanhado
    database.add(usuario)

    # executa o UPDATE necessário sem confirmar definitivamente a operação
    database.flush()

    # atualiza o objeto com o estado que esta no banco
    database.refresh(usuario)

    # devolve o usuario atualizado
    return usuario
# com SQLAlchemy o banco procura na coluna login sem carregar todos usuarios para uma lista python


