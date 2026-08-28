# Sistema de Apostas — Copa do Mundo 2026

## 1. Objetivo

Desenvolver o backend de um sistema de apostas para os jogos da Copa do Mundo de 2026, utilizando arquitetura em camadas, persistência em banco de dados SQL e integração com uma API externa de futebol.

## 2. Regras de negócio

### Cadastro e usuários

- **Maioridade:** apenas usuários com 18 anos completos ou mais podem se cadastrar, com validação pela data de nascimento.
- **Saldo inicial:** todo novo usuário começa com exatamente 100 pontos.
- **Segurança da senha:** a senha deve possuir no mínimo 8 caracteres, incluindo pelo menos uma letra maiúscula, uma letra minúscula, um número e um caractere especial. A senha é armazenada como hash Argon2.
- **Falência:** o usuário não é inativado apenas por apostar todo o saldo. A falência é verificada depois da liquidação: se o saldo continuar igual ou inferior a zero e não existirem outras apostas pendentes, a conta é inativada sem apagar o histórico.
- **Cancelamento voluntário:** o usuário perde o acesso ao sistema, mas seus dados históricos e sua pontuação permanecem visíveis no ranking.

### Apostas e multiplicadores

- **Saldo suficiente:** para registrar ou multiplicar uma aposta, o usuário precisa possuir os pontos necessários.
- **Partida disponível:** somente partidas agendadas aceitam apostas e multiplicações.
- **Bloqueio de exclusão:** uma aposta não pode ser excluída ou alterada. Para realizar outro palpite, o usuário deve criar uma nova aposta.
- **Multiplicação:** uma aposta pendente pode receber fatores `x2`, `x3`, `x4` ou `x5` de forma acumulada, sem limite máximo predefinido, desde que exista saldo suficiente.
- **Débito adicional:** ao multiplicar, o sistema debita somente a diferença entre o valor total anterior e o novo valor total.
- **ODD preservada:** a ODD aceita no cadastro permanece registrada na aposta e não é modificada por apostas posteriores.

### Fórmula oficial das ODDs

As ODDs são recalculadas após cada nova aposta, considerando a quantidade de apostas pendentes em cada lado da partida:

```text
ODD_Time = 1 + (Apostas_Outro_Time / Apostas_Proprio_Time)
```

- **Tratamento de zero:** se um dos lados ainda não possuir apostas, as ODDs da casa e do visitante permanecem em `2.0`, evitando divisão por zero.
- **Contagem:** a fórmula considera a quantidade de apostas, e não a quantidade de pontos apostados.
- **Empate previsto:** palpites de empate recebem ODD `1.0` e não entram na contagem das ODDs de casa e visitante.

### Resultados e ranking

- **Vitória:** o usuário vence somente quando acerta exatamente os gols do time da casa e do visitante. O prêmio é calculado por `Valor_Total_Apostado × ODD_Registrada`.
- **Derrota:** se o resultado real não for empate e o usuário errar o placar exato, a aposta é marcada como perdedora. O valor já debitado permanece definitivamente descontado.
- **Empate real:** todas as apostas da partida são devolvidas integralmente, independentemente do palpite realizado.
- **Ranking:** os usuários são ordenados pelo saldo. Contas inativas continuam visíveis para preservar o histórico.

## 3. Critérios técnicos

- **Arquitetura:** organização em `models`, `repositories`, `services`, `schemas`, `routes` e `integrations`.
- **Persistência:** SQLite com SQLAlchemy ORM, sem espalhar consultas SQL puras pelo projeto.
- **Validação:** schemas Pydantic para entradas e respostas.
- **Integração:** Football Data API para importar e atualizar partidas da Copa do Mundo de 2026.
- **Erros:** exceções controladas e blocos `try/except` para falhas de negócio, persistência e serviços externos.
- **Transações:** operações financeiras utilizam `commit` em caso de sucesso e `rollback` em caso de falha.

## 4. Decisões da implementação

- **Autenticação:** JWT com fluxo OAuth2 Password Bearer.
- **Senhas:** hash Argon2; as senhas originais não são armazenadas.
- **Administração:** operações administrativas exigem JWT e o cabeçalho `X-Admin-Key`.
- **Banco:** SQLite local na aplicação e SQLite em memória nos testes.
- **Testes:** Pytest com banco isolado, cobrindo usuários, apostas, ODDs, liquidação, falência, administração e frontend.
- **Frontend:** interface adicional em HTML, CSS e JavaScript que consome o backend sem duplicar suas regras de negócio.
- **Demonstração:** scripts locais criam partidas previsíveis sem substituir a integração externa.
