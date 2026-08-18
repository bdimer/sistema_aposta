"""Centraliza e valida as configurações usadas pelo backend."""

# Importa os para permitir a leitura das variáveis do sistema operacional.
import os
# Importa Path para montar um caminho absoluto e portável para o banco SQLite.
from pathlib import Path
# Importa load_dotenv para copiar as variáveis do arquivo .env para o ambiente.
from dotenv import load_dotenv
# Importa BaseModel para validar os tipos das configurações da aplicação.
from pydantic import BaseModel, ConfigDict

# Calcula a pasta raiz do projeto subindo um nível a partir da pasta app.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Lê o arquivo .env localizado na raiz, caso ele exista.
load_dotenv(PROJECT_ROOT / ".env")
# Monta a URL padrão do SQLite usando um caminho para sistema_aposta.db.
DEFAULT_DATABASE_URL = f"sqlite:///{(PROJECT_ROOT / 'sistema_aposta.db').as_posix()}"


# Declara um modelo Pydantic para garantir os tipos corretos das configurações.
class Settings(BaseModel):
    """Representa configurações validadas e imutáveis da aplicação."""

    # Impede que uma configuração seja alterada acidentalmente após a criação.
    model_config = ConfigDict(frozen=True)
    # Define o nome mostrado na documentação automática da API.
    app_name: str = "Sistema de Apostas - Copa do Mundo 2026"
    # Permite trocar o banco por variável de ambiente, mantendo SQLite como padrão.
    database_url: str = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    # Lê a chave da API sem obrigá-la na inicialização do banco local.
    football_api_key: str | None = os.getenv("API_KEY")
    # Lê a chave usada para assinar e verificar os tokens de autenticação
    jwt_secret: str = os.getenv(
        "JWT_SECRET",
        "CHAVE_INSEGURA_APENAS_PARA_DESENVOLVIMENTO",
    )
    # Define o algoritmo criptográfico usado para assinar o JWT
    jwt_algorithm: str = "HS256"

    # Determina por quantos minutos o usuário permanecerá autenticado
    access_token_expire_minutes: int = 60



# Cria uma única instância validada para ser importada pelos demais módulos.
settings = Settings()
