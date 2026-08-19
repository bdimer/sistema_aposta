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