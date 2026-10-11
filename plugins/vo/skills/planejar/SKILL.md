---
name: planejar
description: Use para planejar a implementação de uma história do View Office com spec aprovada. O agente planejador divide a história em sub-tasks verticais com arquivos previstos e as skills de cada uma; o comando mostra o plano inteiro e, com uma confirmação, cria o package, as sub-tasks, as dependências e as propostas de ADR e de skill, e devolve a primeira sub-task pronta.
argument-hint: "<chave da história ou do épico>"
disable-model-invocation: true
allowed-tools: Bash(sh *scripts/execucao.sh*) Bash(sh *scripts/pre-condicoes.sh*) Bash(sh *scripts/regras.sh*)
---

# /vo:planejar

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/execucao.sh" planejar "${CLAUDE_SESSION_ID}" "$ARGUMENTS"`

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/pre-condicoes.sh" "${CLAUDE_PROJECT_DIR}" --git`

Argumentos: `$ARGUMENTS` (a chave da história, ou de um épico).

Se a última linha acima for `situacao=bloqueado`, diga o que falta (`config=ausente`: rodar `/vo:configurar`; `git=fora-de-repositorio` ou `git=ausente`: rodar dentro do repositório do projeto, com o git instalado) e pare. O planejamento lê o código, então precisa do repositório.

## Regras

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/regras.sh" transparencia skills-do-projeto propostas estados-do-fluxo`

## Passos

1. **Qual história.** `obter_item` da chave.
   - **Épico**: liste as histórias dele com o estado da spec de cada uma e pergunte qual planejar. Uma história por vez.
   - **História** (`task`): siga. Sub-task não se planeja; sugira `/vo:implementar`.
2. **Pré-condições.**
   - **Spec**: precisa estar `aprovada` (`## Spec` › **Estado**). Se não estiver, mostre o estado e ofereça: rodar `/vo:refinar <chave>` (recomendado) ou seguir assim mesmo, com as pendências registradas como suposições do plano. Seguir só com escolha explícita da pessoa.
   - **Plano existente**: `listar_itens` com `tipo: subtask` e `pai` = a história. Se já houver sub-tasks, mostre-as e ofereça completar o plano (só o que falta, sem duplicar) ou parar.
   - `obter_processo`: permissões (precisa de `criar` no kanban), colunas, skills de processo e índice das skills.
3. **Planejador.** Chame o agente `planejador` deste plugin (`vo:planejador`). No prompt, passe: `projeto_id`, a chave, o texto e a spec inteiros, as skills de processo inteiras, o índice das skills, as sub-tasks existentes e, se a pessoa escolheu seguir sem spec aprovada, as pendências como suposições.

   Confira a resposta antes de mostrar: toda regra `R<n>` não riscada aparece na **Cobertura**; nenhuma dependência forma ciclo; toda sub-task tem arquivos previstos e a seção **Skills** (mesmo que seja "sem skill").
4. **Mostrar o plano inteiro**, de uma vez:
   - o package e a branch base;
   - as sub-tasks em ordem, com cobertura, entrega, arquivos, skills, testes e dependências;
   - a tabela de cobertura;
   - ADRs e skills a propor, com o conteúdo completo;
   - riscos e suposições.

   Ajuste com a pessoa até ela aprovar o plano.
5. **Gravar**, com uma confirmação para o lote (`shared/transparencia.md`), nesta ordem:
   - `criar_package` com o nome do plano, se ainda não existir no quadro (`obter_quadro`), e `atualizar_item` da história com esse `package`;
   - propostas de skill (`propor_skill`) **sem** `item`: o padrão precisa valer antes da implementação, então vale assim que for aprovado. Guarde a `PROP-N` de cada uma;
   - `criar_item` de cada sub-task, em ordem: `tipo: subtask`, `pai` = a história, `package`, título do plano e a descrição abaixo; as impedidas vão para a coluna de impedimento, se houver (`shared/estados-do-fluxo.md`);
   - `criar_ligacao` de cada dependência: `de` = a sub-task que depende, `para` = a que ela precisa, `tipo: depende_de`, com o contexto do que ela precisa;
   - ADRs (`propor_decisao`) com `item` = a história e **sem** `itens` (que criaria ligações genéricas `relacionado`); depois, `criar_ligacao` de cada sub-task que aplica a ADR para ela, com `tipo: implementa`.

   Descrição de cada sub-task:

   ```markdown
   **História:** <chave> · cobre <R1, R2>

   ### Entrega
   - [ ] <o que fica funcionando, verificável>

   ### Arquivos previstos
   - `<caminho>` (novo|alterado)

   ### Skills
   - `<nome> › <Seção>` (casou `<caminho>`)
   - sem skill: `<caminho>`

   ### Testes
   - <cenário da spec> → <tipo de teste>

   ### Checks
   - <os da skill de processo>

   ### Impedimento
   - <nenhum, ou: aguarda a aprovação da PROP-N (skill `<nome>`)>
   ```

   Depois, `listar_itens` com `pai` = a história: confira que as sub-tasks existem, com o package, e que as dependências estão nas ligações (`obter_item` de cada uma que depende de outra).
6. **Devolver.** O package, as sub-tasks com a chave e a ordem, as propostas criadas (`PROP-…`, `ADR-…`) e a **primeira sub-task pronta**: sem dependência pendente e sem impedimento. Próximo passo: `/vo:implementar <chave>`. Se todas estiverem impedidas, diga quem precisa aprovar o quê (`/vo:aprovar`).

## O que grava

No VO: o package, as sub-tasks com as dependências e propostas de skill e de ADR. Nada no repositório: a branch é criada no `/vo:implementar`.

## Não faz

- Mudar a spec. Se o planejamento mostrar um furo na spec, pare, explique e sugira `/vo:refinar <chave>`.
- Escrever código, criar a branch ou mover a história para desenvolvimento.
- Aprovar as propostas que criou.
