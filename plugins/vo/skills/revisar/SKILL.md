---
name: revisar
description: Use para revisar a implementação da branch atual contra a base do projeto antes do PR. Usa o agente revisor com o diff, a spec e as skills dos arquivos; cada apontamento cita a regra que o sustenta. Conduz a correção um apontamento por vez, registra discordâncias com o motivo da pessoa e grava o resultado como comentário na história, com o sha revisado.
argument-hint: "[chave da história ou sub-task]"
disable-model-invocation: true
allowed-tools: Bash(sh *scripts/execucao.sh*) Bash(sh *scripts/pre-condicoes.sh*) Bash(sh *scripts/regras.sh*)
---

# /vo:revisar

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/execucao.sh" revisar "${CLAUDE_SESSION_ID}" "$ARGUMENTS"`

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/pre-condicoes.sh" "${CLAUDE_PROJECT_DIR}" --git`

Argumentos: `$ARGUMENTS` (opcional: a chave da história ou de uma sub-task do package).

Se a última linha acima for `situacao=bloqueado`, diga o que falta e pare.

## Regras

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/regras.sh" transparencia skills-do-projeto propostas revisao`

## Git

Só leitura (`status`, `diff`, `log`, `fetch`, `merge-base`, `add -N`), mais `add` e `commit` dos arquivos corrigidos, com confirmação. Nunca `push`, `reset --hard`, `clean`, `rebase` nem `--force`.

## Passos

1. **Contexto.** `obter_processo` (quem é você, base da skill de processo, checks). A branch atual é o package. Ache os itens dele: a chave dos argumentos (e o `pai` dela), senão as chaves nas mensagens de `git log origin/<base>..HEAD`, senão os itens com esse `package` (`shared/revisao.md`). `obter_item` da história, para a spec, e das sub-tasks.
2. **Diff.** `git fetch`, `merge-base`, `git add -N` dos arquivos novos e `git diff <merge-base>`. Sem diff, diga isso e pare. Com mudanças não commitadas, avise que a revisão vai ser **provisória**.
3. **Skills.** `skills_para_arquivos` com os arquivos do diff. Guarde o conteúdo.
4. **Revisor.** Chame o agente `revisor` deste plugin (`vo:revisor`) com o diff, os arquivos, a spec (regras e cenários), as sub-tasks e as skills. Se houver um comentário de revisão anterior na história, passe os apontamentos dele também. Descarte os apontamentos sem `arquivo:linha` ou sem regra citada, dizendo quantos caíram.
5. **Mostrar**: o veredito, os apontamentos por severidade (problema, regra, sugestão), a cobertura da spec e as sugestões.
6. **Corrigir, um apontamento por vez** (`bloqueia` e `importante`). Para cada um, pergunte:
   - **corrigir**: faça a mudança mínima que atende à regra citada, siga as skills do arquivo e mostre o diff dela;
   - **não se aplica**: peça o motivo e registre com as palavras da pessoa;
   - **deixar aberto**: o apontamento continua aberto e a revisão não fica limpa.

   Depois das correções, rode os checks do projeto. Com uma confirmação, faça um commit local dos arquivos corrigidos: "corrige apontamentos da revisão" e a chave. Ofereça revisar de novo: uma rodada nova sobre o HEAD novo, passando os apontamentos anteriores.
7. **Gravar o resultado**, com uma confirmação: `comentar_item` na história com o comentário de revisão de `shared/revisao.md`. O sha é o do HEAD revisado. A situação de cada apontamento é `corrigido em <sha>`, `não se aplica: <motivo>` ou `aberto`. Confira com `obter_item`.
8. **Devolver.** O veredito e o próximo passo:
   - **limpa** no HEAD, sem mudanças pendentes: `/vo:preparar-pr`;
   - com apontamentos abertos: corrigir e rodar `/vo:revisar` de novo;
   - provisória: commitar e revisar de novo.

## O que grava

No repositório: as correções e um commit local, se a pessoa aceitar. No VO: o comentário de revisão na história.

## Não faz

- Push, PR ou mover itens: isso é o `/vo:preparar-pr`.
- Corrigir sem perguntar, juntar apontamentos numa correção só ou inventar o motivo de uma discordância.
