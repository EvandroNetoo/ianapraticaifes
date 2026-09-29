# Contexto operacional para IA

## Missão

Construir o ProposalFlow, um MVP comercial de propostas: cadastro de clientes, composição de proposta, cálculo confiável, link público e aceite/recusa.

## Fase atual

Checkpoint inicial da oficina. Há especificação e decisões, mas não há implementação. O primeiro objetivo de execução está em `prompts/01-implementar-mvp.md`.

## Fonte de verdade

1. Pedido atual do usuário.
2. `SPEC.md`.
3. `AGENTS.md`.
4. Decisões registradas em `docs/`.
5. Testes e comportamento executável.

Se houver conflito, torne-o explícito antes de mudar comportamento.

## Decisões fixadas

- Python e FastAPI no backend.
- HTML, CSS e JavaScript simples no frontend.
- SQLite e SQLAlchemy para persistência.
- pytest para testes.
- Dinheiro representado por `Decimal` ou centavos inteiros.
- Cálculos e transições de status validados no servidor.
- Token público aleatório e não enumerável.
- Interface e mensagens em português do Brasil.

## Não objetivos do MVP

Sem autenticação, multi-tenancy, pagamentos, mensagens externas, PDF, assinatura eletrônica, IA dentro do produto ou deploy obrigatório.

## Invariantes centrais

- Uma proposta possui cliente e pelo menos um item.
- Quantidade e preço são positivos.
- Desconto fica entre 0% e 100%.
- Total é derivado dos itens e do desconto.
- Apenas propostas enviadas podem receber decisão pública.
- A página pública não revela dados administrativos.

## Definição de concluído

Uma tarefa só termina quando o comportamento pedido existe, a documentação aplicável está coerente e as validações relevantes foram executadas com resultado relatado.
