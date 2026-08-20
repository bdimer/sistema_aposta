# Scripts de demonstração

Esta pasta contém utilitários para criar partidas previsíveis sem depender da API externa durante os testes manuais.

## Preparação da apresentação

```powershell
python -m scripts.preparar_apresentacao
```

Cria, sem duplicação:

- uma partida encerrada para consulta de resultados;
- três partidas agendadas para apostas e cenários opcionais.

## Cenários gerais

```powershell
python -m scripts.criar_partida_demo
```

Cria partidas adicionais para testar vitória, empate e falência.

Os scripts utilizam o mesmo banco configurado pela aplicação. Eles não apagam usuários, partidas ou apostas existentes.

Para a documentação completa, consulte o [`README.md`](../README.md) e a [`ARQUITETURA.md`](../ARQUITETURA.md).
