# Sistema de Apostas — Copa do Mundo 2026

Backend de um sistema de apostas esportivas desenvolvido com FastAPI, Pydantic, SQLAlchemy e banco de dados SQLite.

O sistema permite cadastrar usuários, importar partidas, registrar e multiplicar apostas, calcular ODDs dinâmicas, liquidar resultados e gerar um ranking.

## Tecnologias

- Python 3.14
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- JWT
- Argon2
- Pytest
- Football Data API

## Estrutura

```text
app/
├── integrations/   # Comunicação com serviços externos
├── models/         # Tabelas SQLAlchemy
├── repositories/   # Consultas ao banco
├── routes/         # Endpoints FastAPI
├── schemas/        # Validação Pydantic
├── services/       # Regras de negócio
├── config.py
├── database.py
└── main.py
scripts/            # Cenários de demonstração
tests/              # Testes automatizados
```

O fluxo principal é:

```text
Rota → Schema → Serviço → Repositório → Modelo → Banco
```

## Regras implementadas

- Cadastro permitido somente para maiores de 18 anos.
- Saldo inicial de 100 pontos.
- Senha com requisitos de complexidade e hash Argon2.
- Autenticação por JWT.
- Inativação sem exclusão do histórico.
- Bloqueio de apostas sem saldo.
- Proibição de excluir apostas.
- Multiplicação acumulada por `x2`, `x3`, `x4` ou `x5`.
- ODD preservada no momento da aposta.
- Recálculo das ODDs conforme a quantidade de apostas.
- Pagamento por placar exato e ODD registrada.
- Devolução integral em empate real.
- Falência somente com saldo zero e sem apostas pendentes.
- Ranking incluindo usuários inativos.

## Fórmula das ODDs

```text
ODD_Time = 1 + (Apostas_Outro_Time / Apostas_Proprio_Time)
```

Quando algum dos lados ainda não possui apostas, ambas as ODDs permanecem em `2.0`.

A ODD salva em uma aposta não é alterada por apostas posteriores.

## Configuração

Crie o ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Copie `.env.example` para `.env` e informe:

```env
API_KEY=SUA_CHAVE_FOOTBALL_DATA
JWT_SECRET=SUA_CHAVE_JWT
ADMIN_KEY=SUA_CHAVE_ADMINISTRATIVA
```

O `.env` não deve ser enviado ao Git.

## Execução

```powershell
python -m uvicorn app.main:app --reload
```

Acesse:

- Swagger: `http://127.0.0.1:8000/docs`
- Verificação: `http://127.0.0.1:8000/health`

## Partidas de demonstração

Como a Copa de 2026 já terminou, é possível criar partidas futuras para demonstrar apostas:

```powershell
python -m scripts.criar_partida_demo
```

O script não duplica cenários existentes.

## Operações administrativas

Sincronização e liquidação exigem:

```text
Authorization: Bearer <token>
X-Admin-Key: <chave administrativa>
```

Usuários comuns não conseguem executar essas operações sem a chave.

## Testes

Execute:

```powershell
python -m pytest -v
```

A suíte cobre:

- cadastro e saldo inicial;
- maioridade;
- senha;
- duplicidade de CPF;
- login e JWT;
- inativação;
- ODDs;
- multiplicação;
- vitória e derrota;
- empate;
- falência;
- proteção administrativa.

Os testes usam SQLite em memória e não modificam o banco da aplicação.

## Documentação adicional

Consulte [`ARQUITETURA.md`](ARQUITETURA.md) para detalhes sobre camadas, relacionamentos e segurança.