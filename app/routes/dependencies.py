"""Define dependências compartilhadas pelas rotas da aplicação."""

# Importa Annotated para associar python a dependencia FastAPI
from typing import Annotated

# Importa recursos usados para receber dependencias e gerar erros HTTP
from fastapi import Depends, HTTPException, status

#Importa o leitor do padrão Authorization: Bearer <token>
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.usuario import Usuario

from app.repositories.usuario_repository import(
    buscar_usuario_por_id #procura usuario pela chave primaria
)
#importa a função que valida o JWT e extrai seu usuario
from app.services.security import obter_usuario_id_token

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