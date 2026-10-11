---
name: vo-fundamentos
description: Use sempre que trabalhar no View Office (VO) pelas ferramentas do servidor MCP vo, dentro ou fora de um comando /vo:*. Explica como o VO organiza projetos, quadros, itens (épico, task, sub-task, pergunta), packages, documentação, grafo de ligações, skills, propostas e métricas, como referenciar cada coisa e onde fica gravado cada artefato do fluxo.
user-invocable: false
---

# Como o VO organiza o trabalho

O View Office (VO) é a fonte única do estado do trabalho. Tudo o que o plugin produz fica nele; no repositório só fica `.claude/vo.json`, que diz o projeto e o quadro.

## Projeto, quadro e itens

- **Projeto** tem uma equipe com permissões por módulo: `kanban`, `documentacao` e `skills`. As ações são `visualizar`, `criar`, `editar`, `deletar`, `aprovar` (não existe no kanban) e `configurar`.
- **Quadro** (prefixo, ex.: `VO`) tem colunas, cada uma com uma categoria: `pendente`, `em_andamento` ou `concluido`.
- **Itens** têm chave (`VO-12`) e tipo:
  - `epico` agrupa tasks;
  - `task` é a história, a unidade que se refina, planeja e entrega;
  - `subtask` é um pedaço da task, a unidade que se implementa;
  - `pergunta` é filha de uma task ou sub-task, atribuída a quem decide; não tem coluna, tem situação (aberta ou respondida) e resposta.
- **Package** é uma branch do git. As sub-tasks de um mesmo package vão juntas para um PR.
- **Sprint** agrupa itens num período.

## Documentação e grafo

- **Domínios** (`dominio:Nome`): glossário e regras de negócio, versionados.
- **Decisões** (`ADR-N`): decisões técnicas, de `proposta` a `aceita`, `rejeitada`, `substituida` ou `depreciada`.
- **Relatórios**: o que foi feito numa data, ligado aos itens.
- **Grafo**: itens, decisões, domínios, relatórios e skills ligados por tipo (`implementa`, `depende_de`, `bloqueia`, `motivou`, `afeta`, `documenta`, `relacionado`…) e com contexto. Antes de trabalhar num item, `obter_vizinhanca` mostra o que está ligado a ele; ao criar algo relacionado, `criar_ligacao` com contexto.

## Skills e propostas

- **Skills** (`skill:nome`): o conhecimento do projeto. Como carregar: `${CLAUDE_PLUGIN_ROOT}/shared/skills-do-projeto.md`.
- **Propostas** (`PROP-N`): mudanças em skills, domínios e ADRs passam por proposta, aprovada por uma pessoa e aplicada quando o item ligado é concluído. Como propor: `${CLAUDE_PLUGIN_ROOT}/shared/propostas.md`.

## Onde cada artefato do fluxo fica

| Artefato | Onde, no VO |
| --- | --- |
| História | item `task`, sob um `epico` |
| Spec (refinamento) | descrição da task, seção `## Spec` (`${CLAUDE_PLUGIN_ROOT}/shared/formato-da-spec.md`) |
| Dúvidas | itens `pergunta` filhos da task |
| Plano | sub-tasks da task, num package, com ligações `depende_de` |
| Andamento e revisão | comentários no item |
| Entrega | relatório ligado aos itens, e o PR no comentário |

## Referências que as ferramentas aceitam

Itens por chave (`VO-12`), decisões por `ADR-N`, domínios por `dominio:Nome`, relatórios por `relatorio:<id>`, skills por `skill:nome`, propostas por `PROP-N`, colunas, labels, packages e sprints por nome, pessoas por e-mail ou `eu`. O `projeto_id` está em `.claude/vo.json`.

## Métricas

O VO registra cada chamada (sem o conteúdo) para a aba Métricas. Durante um comando `/vo:*`, o plugin marca as chamadas com o comando e a execução; não envie nem altere o argumento `_vo` por conta própria.
