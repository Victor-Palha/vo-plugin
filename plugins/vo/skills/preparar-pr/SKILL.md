---
name: preparar-pr
description: Use quando o package estiver implementado e revisado, para abrir ou atualizar o pull request no GitHub. Exige sub-tasks feitas, árvore limpa, checks verdes e a última revisão limpa no HEAD; faz o push, cria ou edita o PR para a base da skill de processo com a descrição gerada, move os itens para a coluna de revisão, registra o relatório ligado aos itens e lista as propostas que serão aplicadas quando os itens concluírem.
argument-hint: "[chave da história]"
disable-model-invocation: true
allowed-tools: Bash(sh *scripts/execucao.sh*) Bash(sh *scripts/pre-condicoes.sh*) Bash(sh *scripts/regras.sh*)
---

# /vo:preparar-pr

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/execucao.sh" preparar-pr "${CLAUDE_SESSION_ID}" "$ARGUMENTS"`

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/pre-condicoes.sh" "${CLAUDE_PROJECT_DIR}" --git --gh`

Argumentos: `$ARGUMENTS` (opcional: a chave da história).

Se a última linha acima for `situacao=bloqueado`, diga o que falta (`gh=…`: instalar e autenticar o GitHub CLI com `gh auth login`) e pare.

## Regras

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/regras.sh" transparencia propostas estados-do-fluxo revisao`

## Git e GitHub

Pode: `status`, `log`, `fetch`, `push -u origin <package>`, `gh pr view`, `gh pr create` e `gh pr edit`. Nunca: `push --force`, push para a base, merge do PR, `reset`, `rebase`.

## Passos

1. **Contexto.** `obter_processo` (base e convenções da skill de processo, colunas). A branch atual é o package; ache a história e as sub-tasks dele (`shared/revisao.md`). A branch não pode ser a base.
2. **Pré-condições** (só leitura). Se alguma falhar, mostre o que falta e o comando que resolve, e pare:
   - **árvore limpa**: `git status --porcelain` vazio;
   - **sub-tasks feitas**: cada sub-task da história tem commit na branch (`git log origin/<base>..HEAD` com a chave) ou já passou do desenvolvimento. Se faltar alguma, rode `/vo:implementar <chave>`;
   - **revisão**: o comentário de revisão mais recente da história tem o sha do HEAD (`git rev-parse --short HEAD`) e o resultado `limpa`. Senão, rode `/vo:revisar`;
   - **checks**: rode os checks da skill de processo agora; precisam passar;
   - **PR existente**: `gh pr view <package> --json url,state,baseRefName`. Se houver um PR aberto, ele é editado, não duplicado.
3. **Preparar**, sem gravar:
   - **título**: no formato da skill de processo; sem formato, `<tipo>: <título da história> (<chave>)`;
   - **descrição**:
     - o que muda, na linguagem da história;
     - os itens, com chave e título;
     - as regras da spec entregues, com os testes que as provam;
     - os checks;
     - a revisão (sha e resultado);
     - as suposições aceitas;
     - as **propostas** ligadas aos itens (`obter_item` › `propostas`), com a situação de cada uma. As aprovadas são aplicadas quando o item chegar à coluna concluída; as abertas ainda precisam de `/vo:aprovar`;
   - **coluna de revisão** de cada item: a da skill de processo. Sem ela, pergunte uma vez (`shared/estados-do-fluxo.md`);
   - **relatório** (`criar_relatorio`): título "<chave>: <título da história>", com o que foi feito, as decisões, o PR e as propostas. `itens` = a história e as sub-tasks.
4. **Mostrar tudo e confirmar uma vez**:
   - o push (`git push -u origin <package>`);
   - o PR, criado ou editado, com base, título e descrição inteira;
   - as movimentações;
   - o relatório;
   - um comentário na história com o link do PR.
5. **Executar, nesta ordem, parando na primeira falha**:
   1. push;
   2. `gh pr create --base <base> --head <package>`, ou `gh pr edit`;
   3. `mover_item` de cada item para a coluna de revisão;
   4. `criar_relatorio`;
   5. `comentar_item` na história com o link.

   Confira com `gh pr view --json url,state,baseRefName,headRefName` e `obter_item`.
6. **Devolver.** A URL do PR, os itens movidos, o relatório e as propostas que aguardam aprovação (`/vo:aprovar`). Diga também que, quando o PR for integrado e os itens chegarem à coluna concluída, as propostas aprovadas são aplicadas.

## O que grava

No GitHub: o push da branch e o PR. No VO: as colunas dos itens, o relatório e um comentário com o link.

## Não faz

- Fazer o merge do PR, mover itens para concluído ou aprovar propostas.
- Abrir PR sem a revisão limpa no HEAD.
