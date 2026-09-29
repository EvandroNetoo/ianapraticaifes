# Roteiro da oficina

## Mensagem central

A oficina não é sobre assistir uma IA gerar código. É sobre transformar um objetivo em software verificável, acompanhar decisões e manter responsabilidade humana sobre o resultado.

## Demonstração principal - aproximadamente 47 minutos

| Bloco | Tempo | Resultado |
|---|---:|---|
| Chatbot, assistente e agente | 3 min | Diferenciar papéis e níveis de autonomia |
| Quando usar agente | 2 min | Escolher a menor ferramenta adequada |
| Apresentar o ProposalFlow | 3 min | Tornar problema e fluxo concretos |
| Mostrar o repositório | 3 min | Explicar contexto persistente |
| Abrir a especificação | 4 min | Definir produto, regra e aceite |
| Mostrar AGENTS e evidências | 3 min | Contrastar contexto com prompt momentâneo |
| Entregar o objetivo | 6 min | Agente lê, planeja, implementa e valida |
| Ler a estrutura | 4 min | Avaliar invariantes, acoplamento e risco |
| Provar o fluxo | 4 min | Exercitar UI e testes, inclusive falhas |
| Introduzir mudança | 6 min | Analisar e implementar imutabilidade |
| Revisão por outro papel | 4 min | Buscar bugs, edge cases e violações |
| Papel humano | 3 min | Separar execução de responsabilidade |
| Desafio final | 2 min | Propor construção com problema real e evidência |

Depois da demonstração, reserve tempo para perguntas, debate e experimentação dos participantes.

## Pontos a enfatizar

- Um prompt grande não substitui uma especificação persistente.
- O agente recebe um objetivo; não precisa ser microgerenciado arquivo por arquivo.
- Teste verde prova apenas o que foi testado, não que a interpretação está correta.
- Mudança de requisito revela se a arquitetura preserva coerência.
- Uma segunda IA é outro olhar, não uma autoridade final.
- Implementação ficou mais barata; validação e responsabilidade não.

## Mudança ao vivo

Só revele `prompts/02-mudanca-imutabilidade.md` depois que o MVP inicial estiver funcionando:

> Uma proposta aceita não pode mais ser alterada.

Peça primeiro análise de impacto. Não enumere banco, domínio, API, UI e testes; observe se o agente descobre essas superfícies.

## Plano de contingência

- Mantenha um checkpoint funcional antes da apresentação.
- Tenha banco de exemplo e testes prontos em um checkpoint separado.
- Se a implementação atrasar, mostre a análise e a validação em vez de esconder o problema.
- Não dependa de APIs pagas ou serviços externos para o fluxo principal.

## Desafio final

Cada participante ou dupla deve escolher:

1. um problema real que alguém usaria;
2. um repositório como memória operacional;
3. uma especificação com critérios de aceite;
4. uma tecnologia ou domínio que ainda não domina;
5. uma demonstração funcionando como evidência.
