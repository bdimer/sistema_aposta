
"""Define dependências compartilhadas pelas rotas da aplicação."""


from typing import Annotated
from fastapi import (
    Depends, Header, HTTPException, status,
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.repositories.usuario_repository import(
    buscar_usuario_por_id #procura usuario pela chave primaria
)
from app.services.security import obter_usuario_id_token
from app.config import settings
from secrets import compare_digest


#informa swagger onde cliente pode conseguir token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/usuarios/login"
)

#cria um tipo reutilizavel para receber sessão do banco
DatabaseDependency = Annotated[
    Session,
    Depends(get_db),
]

# Cria um tipo reutilizavel para receber o token Bearer
TokenDependency = Annotated[
    str,
    Depends(oauth2_scheme),
]

#Busca o usuario pelo token enviado na requisição
def obter_usuario_atual(
        database: DatabaseDependency,
        token: TokenDependency,
) -> Usuario:
    """Retorna o usuário autenticado ou responde com HTTP 401."""
    #tenta validar token e recuperar ID armazenado
    usuario_id = obter_usuario_id_token(token)

    if usuario_id is None: #rejeita tokens invalidos
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    #procura no banco usuario identificado pelo token
    usuario = buscar_usuario_por_id(
        database,
        usuario_id,
    )

    if usuario is None: #rejeita tokens que indicam conta inexistente
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.ativo: #impede conta inativa de usar token antigo
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo.",
        )
    return usuario

#Cria um tipo reutilizavel para representar o usuario autenticado
UsuarioAtualDependency = Annotated[
    Usuario,
    Depends(obter_usuario_atual),
]


#-----
# Valida o cabeçalho administrativo enviado na requisição.
def validar_admin_key(
    admin_key: Annotated[
        str | None,
        Header(alias="X-Admin-Key"),
    ] = None,
) -> str:
    """Aceita somente a chave administrativa configurada no servidor."""

    if admin_key is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chave administrativa não informada.",
        )

    chave_valida = compare_digest(
        admin_key,
        settings.admin_key,
    )

    if not chave_valida:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chave administrativa inválida.",
        )
    return admin_key


# Cria um tipo reutilizável para operações administrativas.
AdminDependency = Annotated[
    str,
    Depends(validar_admin_key),
]