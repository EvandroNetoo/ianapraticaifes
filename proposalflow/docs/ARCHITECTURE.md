# Arquitetura de referência

## Objetivo

Manter o MVP simples o suficiente para uma oficina e estruturado o suficiente para tornar regras, testes e mudanças compreensíveis.

## Visão geral

```text
Navegador
  -> rotas FastAPI
      -> serviços/regras de negócio
          -> modelos e sessão SQLAlchemy
              -> SQLite

FastAPI
  -> templates HTML
  -> CSS/JavaScript
```

## Componentes do domínio

- `Customer`: representa o cliente da proposta.
- `Proposal`: agrega cliente, desconto, status, datas e decisão.
- `ProposalItem`: guarda descrição, quantidade e preço unitário.
- `PublicToken`: pode ser um campo único da proposta ou uma entidade separada; a escolha deve preservar unicidade, rotação futura e não enumeração.

## Estrutura inicial sugerida

```text
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── services/
│   └── proposals.py
├── routes/
│   ├── admin.py
│   └── public.py
├── templates/
└── static/

tests/
├── conftest.py
├── test_calculations.py
├── test_status_transitions.py
└── test_public_flow.py
```

Essa estrutura é uma referência, não uma obrigação. Divida arquivos apenas quando houver responsabilidade real a separar.

## Fronteiras importantes

### Rotas

Recebem entrada, chamam serviços, traduzem resultados em HTTP e escolhem a resposta. Não devem concentrar cálculo monetário ou máquina de estados.

### Serviços de domínio

Aplicam regras de cálculo, validação e transição. Devem ser testáveis sem depender da interface.

### Persistência

Garante restrições básicas, unicidade do token e integridade referencial. Regras críticas também precisam existir na camada de domínio quando o banco sozinho não expressá-las.

### Templates e JavaScript

Melhoram interação e feedback, mas não são fonte de verdade para valores ou status.

## Princípios

- Uma regra importante deve ter um lugar canônico.
- A página pública usa um token opaco, nunca o ID sequencial.
- O banco de teste é descartável e isolado.
- Migrações podem ser adicionadas quando trouxerem valor real; não são exigência automática do primeiro checkpoint.
- Concorrência em decisões públicas deve ser considerada na implementação e coberta na medida compatível com SQLite e com o escopo da oficina.
