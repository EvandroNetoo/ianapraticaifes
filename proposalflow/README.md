# ProposalFlow

ProposalFlow é o projeto-guia da oficina: um micro-SaaS para cadastrar clientes, montar propostas comerciais, compartilhar um link público e registrar a decisão do cliente.

## Estado atual

Este é o checkpoint inicial da oficina. O contrato do produto e as regras de engenharia estão prontos; a aplicação ainda não foi implementada.

## Leitura obrigatória

1. [SPEC.md](SPEC.md) - requisitos e critérios de aceite.
2. [AGENTS.md](AGENTS.md) - como trabalhar neste repositório.
3. [AI_CONTEXT.md](AI_CONTEXT.md) - contexto resumido para uma nova sessão de IA.
4. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - arquitetura de referência.
5. [docs/DECISIONS.md](docs/DECISIONS.md) - decisões já tomadas e seus motivos.

## Stack definida

- Frontend: HTML, CSS e JavaScript sem framework obrigatório.
- Backend: FastAPI.
- Persistência: SQLite com SQLAlchemy.
- Testes: pytest.

## Resultado esperado do MVP

O fluxo demonstrável deve permitir:

```text
cadastrar cliente
      -> criar proposta e itens
      -> aplicar desconto
      -> gerar link público
      -> abrir como cliente
      -> aceitar ou recusar
```

Os comandos exatos de instalação e execução devem ser adicionados aqui pelo agente quando a implementação existir e estiver validada.
