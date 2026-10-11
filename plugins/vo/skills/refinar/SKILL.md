---
name: refinar
description: Use para refinar uma história do View Office até a spec ficar aprovada, uma rodada por chamada. Lê o que mudou desde a última rodada (respostas, comentários), usa o agente refinador para montar a spec a partir de domínios, ADRs, skills e código, faz a triagem em lote dos cenários e decisões padrão, abre até 5 perguntas para quem decide, propõe as mudanças de documentação ligadas à história e registra a aprovação.
argument-hint: "<chave da história>"
disable-model-invocation: true
allowed-tools: Bash(sh *scripts/execucao.sh*) Bash(sh *scripts/pre-condicoes.sh*) Bash(sh *scripts/regras.sh*)
---

# /vo:refinar

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/execucao.sh" refinar "${CLAUDE_SESSION_ID}" "$ARGUMENTS"`

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/pre-condicoes.sh" "${CLAUDE_PROJECT_DIR}"`

Argumentos: `$ARGUMENTS` (a chave da história, ex.: `APP-24`).

Se a última linha acima for `situacao=bloqueado` com `config=ausente`, peça para rodar `/vo:configurar` e pare.

## Regras

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/regras.sh" transparencia perguntas propostas formato-da-spec estados-do-fluxo`

## Passos

1. **Qual história.** Sem chave nos argumentos, liste as tasks das colunas `pendente` cuja descrição não tem `**Estado:** aprovada` (`listar_itens` com `tipo: task`) e pergunte qual refinar. A história precisa ser `task` ou `subtask`; épico se refina história por história.
2. **Contexto.** `obter_processo` (permissões, colunas, skills de processo e índice das skills), `obter_item` da história (texto, `## Spec`, comentários, ligações) e `listar_itens` com `tipo: pergunta` e `pai` = a história, para ter todas as perguntas com a situação de cada uma; `obter_item` das que foram respondidas desde a última rodada, para ler a resposta.
3. **Em que ponto está.** Pela seção `## Spec`:
   - **sem spec**: rodada 1, estado `rascunho`;
   - **`aprovada`**: diga quem aprovou e quando, e sugira `/vo:planejar <chave>`. Só reabra se a pessoa pedir: o estado volta para `pronta` e a rodada nova registra o motivo;
   - **`aguardando`** sem resposta nova às perguntas que bloqueiam: liste-as com o responsável de cada uma, sugira `/vo:responder-perguntas` a quem decide, e pare;
   - nos outros casos: rodada seguinte à última da tabela **Rodadas**. O que é novo: perguntas respondidas que a tabela ainda não incorporou, comentários posteriores à data da última rodada e mudanças no texto da história.
4. **Refinador.** Chame o agente `refinador` deste plugin (`vo:refinador`). No prompt, passe:
   - `projeto_id`, chave, o texto acima de `## Spec` e a spec atual inteira;
   - o número da rodada e o que é novo (passo 3), com as perguntas e respostas por inteiro;
   - as seções **Formato da spec** e **Perguntas** das regras acima, copiadas inteiras;
   - as permissões e o índice das skills de `obter_processo`.

   Ele devolve a spec proposta, o que mudou, as perguntas candidatas, as decisões padrão, a documentação a propor e as divergências. Confira que toda regra tem origem e que nada acima de `## Spec` mudou.
5. **Triagem em lote.** Mostre num bloco só: o que mudou, os cenários novos, as decisões padrão e as perguntas candidatas. Peça uma resposta para o bloco: "aceito tudo", "aceito, exceto…" (ajustar uma decisão, encaminhar uma decisão como pergunta, descartar uma pergunta) ou "ajustar a spec". Divergências entre fontes vão primeiro, com o que você sugere.
   - Decisão encaminhada vira pergunta e fica `encaminhada (<chave>)` na tabela.
   - **No máximo 5 perguntas novas por rodada.** O que passar disso fica para a próxima ou vira decisão padrão.
   - **Quem decide**: a skill de processo, se disser quem é o PO e quem é o tech lead. Senão, pergunte uma vez, com as pessoas que podem ser responsáveis (`obter_quadro`), e sugira registrar isso na skill de processo com `/vo:propor-skill`.
6. **Gravar**, com uma confirmação para o lote (`shared/transparencia.md`). Na spec mostrada, as perguntas novas aparecem como `P1`, `P2`…; não adivinhe as chaves. Nesta ordem:
   - `criar_item` de cada pergunta: `tipo: pergunta`, `pai` = a história, `responsavel` = quem decide, título e descrição no formato de `shared/perguntas.md`;
   - `atualizar_item` da história com a `descricao` inteira: o texto acima de `## Spec`, **copiado sem nenhuma mudança**, mais a spec nova, com `P1`, `P2`… trocados pelas chaves que o VO devolveu e a linha da rodada na tabela **Rodadas** (data de hoje, perguntas abertas, o que mudou);
   - documentação, conforme `shared/propostas.md` e as permissões: `atualizar_proposta` quando já há proposta aberta do mesmo alvo ligada à história; senão `propor_alteracao_dominio`, `propor_dominio` ou `propor_decisao`, sempre com `item` = a história;
   - mover a história só se a skill de processo indicar uma coluna de refinamento (`shared/estados-do-fluxo.md`).

   Depois, `obter_item` da história: confira que a descrição começa com o texto original e que a spec gravada é a mostrada.
7. **Aprovar.** Se a spec ficou `pronta`, pergunte se a pessoa a aprova agora. Se a skill de processo disser que quem aprova é outra pessoa (o PO, por exemplo), não pergunte: diga quem precisa rodar `/vo:refinar <chave>` para aprovar. Aprovando, com uma confirmação:
   - `atualizar_item`: **Estado:** `aprovada` e **Aprovada por:** `<nome> em <AAAA-MM-DD>` (o nome é o de `obter_processo`), sem mudar mais nada;
   - `comentar_item`: "Spec aprovada por <nome> na rodada <n>.", com as propostas ligadas (`PROP-…`) que serão aplicadas quando a história for concluída.
8. **Devolver.** Estado da spec, perguntas abertas com o responsável de cada uma, propostas criadas ou atualizadas e o próximo passo:
   - `aguardando`: `/vo:responder-perguntas`, por quem decide, e depois `/vo:refinar <chave>`;
   - `pronta`: a aprovação;
   - `aprovada`: `/vo:planejar <chave>`.

## O que grava

No VO: a descrição da história (só a seção `## Spec`), os itens `pergunta`, propostas de documentação ligadas à história e o comentário de aprovação.

## Não faz

- Mudar o texto da história acima de `## Spec`. Se ele precisa mudar, diga isso e deixe a pessoa editar no VO.
- Planejar (dividir em sub-tasks, arquivos, branches): isso é o `/vo:planejar`.
- Responder perguntas em nome de quem decide, ou aprovar propostas.
