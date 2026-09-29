# ProposalFlow v1 - Especificação do produto

## 1. Visão

ProposalFlow é um micro-SaaS para prestadores de serviço, freelancers, pequenas agências e pequenos negócios criarem propostas comerciais profissionais e obterem a decisão do cliente por um link público.

O MVP deve parecer um produto utilizável, não apenas uma coleção de telas CRUD.

## 2. Objetivo do MVP

Uma pessoa deve conseguir cadastrar um cliente, criar uma proposta com vários itens, aplicar desconto, compartilhar a proposta e acompanhar se ela foi aceita ou recusada.

## 3. Escopo funcional

### 3.1 Clientes

- Cadastrar cliente com nome obrigatório.
- Permitir e-mail e nome da empresa como dados opcionais.
- Listar clientes cadastrados.
- Selecionar um cliente ao criar uma proposta.

### 3.2 Propostas

- Criar uma proposta vinculada a um cliente.
- Informar um título ou descrição curta.
- Adicionar um ou mais itens.
- Cada item possui descrição, quantidade e preço unitário.
- Aplicar desconto percentual opcional entre 0% e 100%.
- Calcular subtotal, valor do desconto e total no servidor.
- Exibir histórico/listagem de propostas com cliente, total e status.

### 3.3 Status e transições

Os status válidos são:

```text
rascunho -> enviada -> aceita
                    -> recusada
```

Regras:

- Uma proposta nova começa como `rascunho`.
- Apenas uma proposta válida pode ser marcada como `enviada`.
- Somente uma proposta `enviada` pode ser aceita ou recusada.
- `aceita` e `recusada` são estados finais no MVP.
- Transições inválidas devem ser rejeitadas com mensagem compreensível.

### 3.4 Link público

- Ao enviar uma proposta, o sistema disponibiliza um link público não enumerável.
- O link mostra somente os dados necessários para avaliar a proposta.
- O visitante do link pode aceitar ou recusar uma proposta enviada.
- O link não deve expor identificadores internos, dados administrativos ou outras propostas.
- Uma nova decisão sobre uma proposta já decidida deve ser rejeitada de forma idempotente e segura.

## 4. Regras de negócio

- A proposta deve possuir pelo menos um item.
- Quantidade e preço unitário devem ser maiores que zero.
- Valores monetários não podem usar ponto flutuante binário como fonte de verdade.
- O cliente e os itens informados precisam existir e ser válidos.
- O total é sempre calculado pelo sistema; valores totais enviados pelo navegador não são confiáveis.
- O desconto deve estar no intervalo permitido.
- O total nunca pode ser negativo.
- A decisão pública deve registrar status e data/hora.
- Erros de validação devem preservar os dados digitados quando possível e orientar a correção.

## 5. Experiência mínima

- Interface responsiva e legível em desktop e celular.
- Formulários com rótulos claros, validação e feedback de sucesso/erro.
- Valores exibidos em real brasileiro (`R$`) e português do Brasil.
- Página pública com identidade visual limpa, cliente, itens, subtotal, desconto, total e ações disponíveis.
- Estados vazios devem explicar a próxima ação possível.

## 6. Segurança e privacidade mínimas

- O token público deve ter entropia suficiente e não pode ser sequencial.
- Entradas devem ser validadas no servidor.
- Conteúdo fornecido pelo usuário deve ser escapado ao renderizar HTML.
- A página pública deve seguir minimização de dados.
- Segredos e banco local não devem ser versionados.

## 7. Fora do escopo da v1

- Autenticação e contas de usuário.
- Multi-tenancy ou organizações.
- Pagamentos, Pix ou cobrança recorrente.
- Envio real de e-mail ou WhatsApp.
- PDF, assinatura eletrônica e personalização de marca.
- Integração obrigatória com modelos de IA.
- Dashboard analítico avançado.
- Deploy em produção.

Esses itens não devem ser implementados sem uma mudança explícita de escopo.

## 8. Critérios de aceite

O MVP está pronto quando:

1. A aplicação inicia localmente com instruções reproduzíveis.
2. É possível cadastrar e listar clientes.
3. É possível criar uma proposta com múltiplos itens e desconto válido.
4. Subtotal, desconto e total são calculados corretamente no servidor.
5. É possível enviar a proposta e abrir seu link público.
6. O cliente pode aceitar ou recusar uma proposta enviada.
7. Transições inválidas e entradas inválidas são rejeitadas com respostas adequadas.
8. O histórico mostra o status atualizado da proposta.
9. O fluxo principal possui testes automatizados.
10. A suíte de testes passa em ambiente limpo.

## 9. Cenários obrigatórios de teste

- Cálculo com um e vários itens.
- Cálculo de desconto e limites de 0% e 100%.
- Quantidade, preço e desconto inválidos.
- Proposta sem itens.
- Transições válidas e inválidas entre status.
- Token público existente, inexistente e não enumerável.
- Aceite e recusa pelo link público.
- Repetição da mesma decisão pública.
- Ausência de dados administrativos na página pública.

## 10. Observação para a oficina

Esta especificação representa o requisito inicial. Mudanças apresentadas durante a demonstração só entram no produto depois de uma solicitação explícita e devem atualizar especificação, implementação e testes.
