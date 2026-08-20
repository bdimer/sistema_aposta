# Arquitetura do Sistema de Apostas

O projeto implementa uma API para apostas nos jogos da Copa do Mundo de 2026. O backend utiliza FastAPI, Pydantic, SQLAlchemy e banco SQLite.

## Organização

```text
app/
├── integrations/   # Comunicação com a Football Data
├── models/         # Tabelas e relacionamentos SQLAlchemy
├── repositories/   # Consultas e operações no banco
├── routes/         # Endpoints HTTP
├── schemas/        # Validação Pydantic de entrada e saída
├── services/       # Regras de negócio
├── config.py       # Configurações e variáveis de ambiente
├── database.py     # Engine, sessões e criação das tabelas
└── main.py         # Aplicação FastAPI
scripts/            # Criação de cenários de demonstração
tests/              # Testes automatizados
```

## Fluxo das requisições

```text
Frontend ou Swagger
        ↓
Routes
        ↓
Schemas e dependências
        ↓
Services
        ↓
Repositories
        ↓
Models e SQLite
```

As rotas recebem requisições HTTP. Os schemas Pydantic validam os dados. Os services aplicam as regras de negócio. Os repositories concentram as consultas, enquanto os models representam as tabelas SQLAlchemy.

## Principais componentes

- `usuario_service.py`: cadastro, autenticação, senha, inativação e ranking.
- `aposta_service.py`: saldo, apostas, multiplicação e cálculo das ODDs.
- `resultado_service.py`: liquidação, prêmios, empate e falência.
- `partida_service.py`: criação e atualização de partidas externas.
- `football_api.py`: comunicação e tratamento de erros da Football Data.

## Persistência e segurança

O SQLite armazena usuários, partidas e apostas. O SQLAlchemy realiza o mapeamento ORM e controla as transações com `commit` e `rollback`.

As senhas utilizam hash Argon2. A autenticação utiliza JWT. Operações administrativas exigem um usuário autenticado e o cabeçalho `X-Admin-Key`.

## Testes

Os testes utilizam Pytest e SQLite em memória, mantendo o banco principal isolado. A suíte cobre usuários, apostas, ODDs, liquidação, falência, administração e entrega do frontend.
