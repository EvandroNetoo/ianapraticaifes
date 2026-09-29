# Instruções para agentes

Estas regras valem para todo o diretório `proposalflow/`.

## Antes de alterar qualquer arquivo

1. Leia `SPEC.md`, `AI_CONTEXT.md` e os documentos relevantes em `docs/`.
2. Inspecione o estado real do repositório; não suponha que arquivos ou dependências já existam.
3. Compare o pedido atual com o escopo da especificação.
4. Se houver ambiguidade que altere comportamento de negócio, explicite a suposição antes de implementá-la.

Arquivos em `prompts/` representam etapas da oficina. Não antecipe requisitos de prompts que ainda não foram solicitados.

## Princípios de implementação

- Prefira a solução mais simples que satisfaça `SPEC.md`.
- Não adicione tecnologia, camadas, serviços ou dependências sem necessidade concreta.
- Mantenha regras de negócio fora das rotas e templates sempre que isso melhorar testabilidade.
- Centralize cálculo de subtotal, desconto e total.
- Use `Decimal` ou centavos inteiros para dinheiro; nunca use `float` como fonte de verdade.
- Modele status e transições explicitamente.
- Gere tokens públicos com fonte criptograficamente segura.
- Valide no servidor tudo que afeta regra de negócio, mesmo que também exista validação no navegador.
- Não confie em total, status ou identificadores enviados pelo cliente.
- Não exponha stack traces, segredos ou dados administrativos na interface pública.
- Preserve o escopo do MVP. Não implemente funcionalidades futuras por antecipação.

## Estrutura esperada

A estrutura pode evoluir, mas deve permanecer pequena e compreensível. A referência inicial está em `docs/ARCHITECTURE.md`.

- `app/`: aplicação FastAPI, domínio, persistência, templates e arquivos estáticos.
- `tests/`: testes de unidade e integração.
- `docs/`: decisões e documentação de engenharia.
- `prompts/`: objetivos usados na demonstração.

## Fluxo de trabalho

1. **Entender**: resuma requisitos, invariantes e não objetivos.
2. **Planejar**: identifique impacto, riscos e evidências necessárias.
3. **Implementar**: entregue uma fatia vertical pequena e coerente.
4. **Validar**: execute testes e, quando aplicável, percorra o fluxo pela interface.
5. **Corrigir**: investigue a causa de falhas; não apenas silencie o sintoma.
6. **Documentar**: atualize README, SPEC ou decisões quando o comportamento mudar.
7. **Relatar**: diga o que mudou, como foi validado e quais riscos permanecem.

## Testes e qualidade

- Cada regra de negócio relevante precisa de evidência automatizada.
- Bugs corrigidos devem ganhar teste de regressão.
- Testes devem verificar comportamento observável, não detalhes frágeis de implementação.
- Use banco isolado para testes; não dependa do banco de desenvolvimento.
- Execute toda a suíte antes de declarar a tarefa concluída.
- Se um teste falhar, determine se a implementação ou a expectativa está errada com base na especificação.

## Alterações de escopo

- Não altere silenciosamente requisitos para facilitar a implementação.
- Uma nova regra deve ter análise de impacto antes da mudança.
- Atualize a especificação e os testes junto com o código.
- Preserve comportamentos anteriores, exceto quando a nova regra os substituir explicitamente.

## Revisão

Ao revisar, não faça apenas uma leitura linha a linha. Procure:

- violações da especificação;
- invariantes duplicadas ou ausentes;
- transições de estado incorretas;
- falhas de autorização ou vazamento no link público;
- cálculos monetários inconsistentes;
- condições de corrida e decisões públicas repetidas;
- tratamento de erro enganoso;
- testes que confirmam a implementação, mas não o requisito.

Não trate concordância entre modelos como prova. A fonte de verdade é a combinação de especificação, comportamento observado e evidências reproduzíveis.
