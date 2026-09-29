# IA na prática - IFES

Repositório de apoio para a oficina **Do objetivo ao produto: desenvolvimento com IA sem microgerenciar prompts**.

O projeto-guia da oficina é o [ProposalFlow](proposalflow/README.md), um micro-SaaS para criar, compartilhar e acompanhar propostas comerciais.

## Estrutura

```text
ianapraticaifes/
└── proposalflow/
    ├── SPEC.md          # contrato do produto
    ├── AGENTS.md        # regras para agentes de desenvolvimento
    ├── CLAUDE.md        # ponto de entrada para Claude Code
    ├── AI_CONTEXT.md    # contexto operacional resumido
    ├── ROADMAP.md       # limites do MVP e possíveis evoluções
    ├── app/             # implementação (inicialmente vazia)
    ├── tests/           # evidências automatizadas
    ├── docs/            # arquitetura, decisões e roteiro
    └── prompts/         # objetivos da demonstração
```

## Como usar na oficina

1. Abra `proposalflow/SPEC.md` e discuta o que significa o produto estar correto.
2. Mostre `proposalflow/AGENTS.md` como contexto persistente de engenharia.
3. Entregue ao agente o objetivo em `proposalflow/prompts/01-implementar-mvp.md`.
4. Valide o fluxo real e os testes.
5. Apresente a mudança em `proposalflow/prompts/02-mudanca-imutabilidade.md`.
6. Troque o papel da IA usando `proposalflow/prompts/03-revisar.md`.

O repositório começa deliberadamente com documentação e diretórios vazios. A implementação é parte da demonstração.
