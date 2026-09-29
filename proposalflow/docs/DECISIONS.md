# Registro de decisões

## D-001 - Stack pequena e local

**Decisão:** FastAPI, templates HTML, CSS/JS, SQLite, SQLAlchemy e pytest.

**Motivo:** permite demonstrar frontend, backend, persistência, regras e testes sem exigir infraestrutura externa.

**Consequência:** o MVP roda localmente e a arquitetura deve evitar abstrações de escala prematuras.

## D-002 - Servidor como fonte de verdade

**Decisão:** totais, descontos e transições de estado são calculados e validados no backend.

**Motivo:** valores vindos do navegador podem ser incorretos ou manipulados.

**Consequência:** a interface pode pré-visualizar, mas o valor persistido sempre vem do domínio.

## D-003 - Representação exata de dinheiro

**Decisão:** usar `Decimal` com escala explícita ou centavos inteiros.

**Motivo:** `float` produz erros binários e não é adequado como fonte de verdade monetária.

**Consequência:** conversão e arredondamento precisam ser definidos em um único lugar.

## D-004 - Link público opaco

**Decisão:** acessar propostas públicas por token aleatório de alta entropia.

**Motivo:** IDs sequenciais permitem enumeração e vazamento de propostas.

**Consequência:** o token precisa ser único, indexado e tratado como dado sensível.

## D-005 - Sem autenticação no primeiro MVP

**Decisão:** autenticação e multi-tenancy ficam fora da v1.

**Motivo:** a oficina deve concentrar-se no fluxo comercial e nas regras de negócio.

**Consequência:** esta versão é uma demonstração local, não está pronta para produção pública.

## D-006 - Mudanças entram por requisito, não por antecipação

**Decisão:** agentes não devem implementar funcionalidades de fases futuras sem solicitação.

**Motivo:** a oficina usa evolução de requisito para demonstrar análise de impacto.

**Consequência:** roadmap e prompts futuros informam a apresentação, mas não alteram o contrato vigente por si sós.
