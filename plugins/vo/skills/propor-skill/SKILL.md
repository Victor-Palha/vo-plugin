---
name: propor-skill
description: Use para criar ou mudar uma skill do projeto no View Office (arquitetura, padrão, processo ou glossário), sempre por proposta com embasamento. Acha a skill certa, analisa o impacto (outras skills, itens em aberto, código), mostra o diff e propõe. Num projeto sem skills, o modo inicial analisa o repositório e propõe o primeiro conjunto de skills, com caminhos de código reais como embasamento.
argument-hint: "[mudança desejada, ou \"inicial\"]"
disable-model-invocation: true
allowed-tools: Bash(sh *scripts/execucao.sh*) Bash(sh *scripts/pre-condicoes.sh*) Bash(sh *scripts/regras.sh*)
---

# /vo:propor-skill

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/execucao.sh" propor-skill "${CLAUDE_SESSION_ID}" "$ARGUMENTS"`

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/pre-condicoes.sh" "${CLAUDE_PROJECT_DIR}" --git`

Argumentos: `$ARGUMENTS` (a mudança em texto livre, ou `inicial`).

Se a última linha acima for `situacao=bloqueado`, diga o que falta e pare. A análise lê o código, então precisa do repositório.

## Regras

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/regras.sh" transparencia skills-do-projeto propostas`

## O que é uma boa skill

- **Uma área, uma skill**: um padrão de LiveView, o fluxo de branches, o tratamento de dinheiro. Não misture assuntos.
- **`descricao` diz quando usar**, numa frase que um agente entende sem ler o resto (até 1024 caracteres). Ex.: "Use ao criar ou mudar LiveViews".
- **`paths`** são globs relativos à raiz que casam arquivos que existem. Skill geral (processo, glossário) fica sem `paths`.
- **Conteúdo**: regras curtas e verificáveis, agrupadas em seções `##` (os apontamentos citam `nome › Seção`), com um exemplo do próprio código quando ajudar. Nada que o linter ou o formatter já garantem.
- **Tipos**: `processo` (branches, checks, o que cada coluna significa, quem decide o quê), `arquitetura`, `padrao`, `glossario`, `outro`.

## Passos

1. **Contexto.** `obter_processo` (quem é você, permissões, colunas, skills de processo e índice). Para propor, é preciso ter `criar` em skills; sem essa permissão, diga quem pode conceder e pare. `listar_propostas` com `alvo: skill`, para ver o que já está aberto.
2. **Modo.** Sem nenhuma skill no projeto, ou com `inicial` nos argumentos: **modo inicial** (passos 8 a 11). Senão, **mudança** (passos 3 a 7). Sem argumentos num projeto que já tem skills, pergunte qual mudança.

### Mudança

3. **Entender.** O que muda e o que motivou: um apontamento de revisão, um "não se aplica" recorrente, uma ADR, um item, um incidente. Junte as referências que **já existem** (`shared/propostas.md`).
4. **Achar o alvo.** `listar_skills` (com `busca`) e `obter_skill` das candidatas. Decida entre alterar uma skill, criar uma nova ou arquivar; na dúvida, pergunte. Se já houver uma proposta aberta para a mesma skill, ofereça ajustá-la (`atualizar_proposta`) em vez de abrir outra.
5. **Impacto:**
   - **outras skills** que tratam do mesmo assunto, e se ficam contraditórias;
   - **itens em aberto** ligados à skill (`obter_vizinhanca` de `skill:<nome>`);
   - **código**: quantos arquivos dentro dos `paths` seguem e quantos contrariam a regra nova (Grep), com exemplos de cada.
6. **Escrever** o conteúdo **inteiro** como deve ficar, o embasamento (por que mudar e o que sustenta a mudança) e as referências. Mostre o diff contra a versão atual, o impacto e a recomendação: com `item`, a mudança só vale quando o item for concluído; sem `item`, vale assim que for aprovada.
7. **Gravar**, com uma confirmação: `propor_skill` ou `propor_alteracao_skill` (com `base_versao` = a versão lida). Confira com `obter_proposta` e siga para o passo 12.

### Modo inicial

8. **Ler o repositório**, sem mudar nada:
   - instruções e convenções: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING*`, `README*` e documentação em `docs/`;
   - estrutura: pastas de topo, linguagens e camadas (`Glob`);
   - checks: aliases e scripts (`mix.exs`, `package.json`, `Makefile`), configuração de formatter e linter, workflows de CI;
   - fluxo de branches: `git branch -a`, `git tag`, os merges recentes no `git log`;
   - padrões visíveis: dois ou três arquivos representativos de cada camada e os testes.
9. **Propor o conjunto**, de 3 a 8 skills. Uma de `processo` é obrigatória: branch base, nomes de branch, checks, mensagem de commit e o que cada coluna do quadro significa. As colunas vêm de `obter_processo`; pergunte a correspondência que você não conseguir deduzir. As demais são de arquitetura, padrões e glossário, conforme o que o código mostra. Mostre uma tabela com nome, tipo, `paths`, quando usar e as seções de cada uma. A pessoa escolhe quais seguem.
10. **Detalhar** as escolhidas: conteúdo inteiro, `paths` conferidos com `Glob` (cada glob casa pelo menos um arquivo) e embasamento com as **fontes reais** de cada regra: `CLAUDE.md › Seção`, caminhos de código (`lib/app/x.ex`), configuração. Regra sem fonte no repositório fica de fora ou vira pergunta.
11. **Gravar**, com uma confirmação para o lote: `propor_skill` de cada uma, sem `item`. Confira com `listar_propostas`.

### Fim

12. **Devolver** as propostas (`PROP-N`, skill e tipo) e o próximo passo: alguém com permissão de aprovar skills roda `/vo:aprovar`. Lembre que as skills só passam a valer depois de aprovadas.

## O que grava

No VO: propostas de skill. Nada no repositório.

## Não faz

- Aprovar as próprias propostas, nem editar uma skill sem proposta.
- Inventar regra que o projeto não segue: toda regra tem fonte no repositório, numa decisão ou na pessoa.
