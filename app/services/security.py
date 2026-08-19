

"""Fornece funções para proteger senhas e controlar tokens JWT."""

from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from app.config import settings


# Cria um objeto configurado com o algoritmo de hash recomendado
password_hash = PasswordHash.recommended()


# Transforma uma senha original em um hash seguro
def gerar_hash_senha(senha: str) -> str:
    """Gera um hash irreversível para uma senha recebida."""

    # Executa o Argon2 e devolve o texto que deverá ser salvo no banco
    return password_hash.hash(senha)


# Confere uma senha original com hash armazenado no banco
def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Verifica se a senha informada corresponde ao hash salvo."""

    # O próprio pwlib compara os valores sem precisar descriptografar a senha
    return password_hash.verify(senha, senha_hash)


# Cria um token quye identifica um usuário autenticado.
def criar_access_token(usuario_id: int) -> str:
    """Gera um JWT temporário contendo o ID do usuário."""

    # Obtem o horario atual em UTC para evitar diferenças de fuso horario
    agora = datetime.now(timezone.utc)

    # Calcula quando o token deixará de ser aceito
    expiracao = agora + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    # Monta os dados internos que serão guardados no token
    payload = {
        "sub": str(usuario_id), # sub significa subject e identifica o dono do token
        "iat": agora, # iat informa o instante em que o token foi emitido
        "exp": expiracao, # exp permite que o PyJWT rejeite automaticamente tokens expirados
    }

    # Assina o conteúdo usando a chave secreta e o algoritmo configurado
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

# Extrai o ID de um token válido
def obter_usuario_id_token(token: str) -> int | None:
    """Retorna o ID guardado no JWT ou None quando o token é inválido."""

    # Inicia um bloco protegido porque tokens externos podem estar corrompidos
    try:
        #Verifica a assinatura e a expiração antes de liberar o conteúdo
        payload = jwt.decode( 
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )

        #Recupera o identificador armazenado no campo subject
        usuario_id = payload.get("sub")

        # Rejeita tokens que não possuam o identificador obrigatório
        if usuario_id is None:
            return None

        #Converte o identificador textual do JWT novamente para inteiro
        return int(usuario_id)

    # Captura tokens adulterados, malformados ou expirados
    except (InvalidTokenError, ValueError, TypeError):
        # None permite que a camada de autenticação responda com HTTP 401
        return None