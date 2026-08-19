# Sistema de Apostas — Copa do Mundo 2026

Backend de um sistema de apostas desenvolvido com FastAPI, SQLAlchemy, Pydantic e SQLite. O projeto permite cadastrar usuários, consultar partidas, registrar e multiplicar apostas, calcular ODDs dinâmicas, liquidar resultados e visualizar o ranking.

## Requisitos

- Python 3.14 ou compatível
- Git
- Chave da Football Data API, caso seja utilizada a sincronização externa

## Instalação

Crie e ative o ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Copie `.env.example` para `.env` e configure:

```env
API_KEY=SUA_CHAVE_DA_FOOTBALL_DATA
JWT_SECRET=UMA_CHAVE_SECRETA
ADMIN_KEY=UMA_CHAVE_ADMINISTRATIVA
```

## Execução

Inicie o servidor:

```powershell
python -m uvicorn app.main:app --reload
```

Acesse:

- Frontend: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs
- Verificação: http://127.0.0.1:8000/health

## Dados de demonstração

Para criar partidas previsíveis sem duplicar registros:

```powershell
python -m scripts.preparar_apresentacao
```

O script cria uma partida encerrada e três partidas agendadas para demonstrar vitória, falência e devolução por empate.

## Testes

Execute:

```powershell
python -m pytest -q
python -m compileall -q app scripts tests
```

A suíte utiliza SQLite em memória e não modifica o banco principal.

## Estrutura

- `app/models`: tabelas SQLAlchemy.
- `app/schemas`: validações Pydantic.
- `app/repositories`: acesso ao banco.
- `app/services`: regras de negócio.
- `app/routes`: endpoints FastAPI.
- `app/static`: frontend.
- `tests`: testes automatizados.
- `scripts`: preparação de dados.