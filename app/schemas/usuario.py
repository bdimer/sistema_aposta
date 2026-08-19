"""Define os formatos de entrada e saída relacionados aos usuários."""

from datetime import date, datetime

# Importa Decimal para representar saldo sem imprecisões
from decimal import Decimal

# Importa recursos do pydantic para validar os dados da API.
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Reúne os campos compartilhados no cadastro e em outras operações.
class UsuarioBase(BaseModel):
    """Contém os dados públicos básicos de um usuário."""
    nome: str = Field(min_length=3, max_length=120) #exige nome entre 3 e 120 caracteres

    email: EmailStr #verifica texto tem formato válido

    cpf: str = Field(min_length=11, max_length=14)

    data_nascimento: date 

    login: str = Field(min_length=3, max_length=80)


# Define os dados aceitos na criação de uma conta.
class UsuarioCreate(UsuarioBase):
    """Representa o corpo JSON enviado para cadastrar um usuário."""
    #minimo 8 caracteres, demais regras verificadas pelo serviço de usuários
    senha: str = Field(min_length=8, max_length=128)

#Define os dados que poderão ser alterados na troca de senha
class TrocaSenha(BaseModel):
    """Representa a senha atual e a nova senha escolhida."""
    #compara a senha atual com o hash armazenado
    senha_atual: str = Field(min_length=1, max_length=128)
    #nova senha será validada antes de gerar um novo hash
    nova_senha: str = Field(min_length=8, max_length=128)

#Define os dados recebidos pelo endpoint de autenticação
class UsuarioLogin(BaseModel):
    """Representa as credenciais enviadas durante o login."""
    
    login: str = Field(min_length=3, max_length=80)

    senha: str = Field(min_length=1, max_length=128)

#Define a resposta pública devolvida pela API
class UsuarioResponse(UsuarioBase):
    """Representa um usuário sem expor seu hash de senha."""

    #Permite criar este schema diretamente a partir de um objeto SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

    id: int
    saldo: Decimal
    #Informa se a conta ainda pode acessar o sistema
    ativo: bool
    #Informa quando a conta foi cadastrada
    criado_em: datetime


# Define a resposta específica da consulta de saldo.
class SaldoResponse(BaseModel):
    """Representa os pontos disponíveis do usuário autenticado."""

    # Decimal preserva exatamente o valor armazenado no banco.
    saldo: Decimal


# Define a estrutura devolvida após uma autenticação bem-secedida.
class TokenResponse(BaseModel):
    """Representa o token usado nas futuras rotas protegidas."""

    # Contém o token JWT assinado pelo servidor
    access_token: str

    token_type: str = "bearer" # bearer = portador, cria uma chave de acesso
    

