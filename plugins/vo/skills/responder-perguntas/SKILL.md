---
name: responder-perguntas
description: Use quando a pessoa quiser responder as perguntas abertas que estão com ela no View Office (normalmente o PO ou o tech lead), de todas as histórias ou de uma só. Mostra cada pergunta com o contexto, as opções e a sugestão de quem perguntou, aceita respostas em lote, grava as respostas e oferece propor a mudança de domínio quando a resposta muda uma regra.
argument-hint: "[chave da história, opcional]"
disable-model-invocation: true
allowed-tools: Bash(sh *scripts/execucao.sh*) Bash(sh *scripts/pre-condicoes.sh*) Bash(sh *scripts/regras.sh*)
---

# /vo:responder-perguntas

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/execucao.sh" responder-perguntas "${CLAUDE_SESSION_ID}" "$ARGUMENTS"`

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/pre-condicoes.sh" "${CLAUDE_PROJECT_DIR}"`

Argumentos: `$ARGUMENTS` (opcional: a chave de uma história, para responder só as perguntas dela).

Se a última linha acima for `situacao=bloqueado` com `config=ausente`, peça para rodar `/vo:configurar` e pare.

## Regras

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/regras.sh" transparencia perguntas propostas`

## Passos

1. **Buscar.** Com o `projeto_id` e o `quadro` das linhas acima, `listar_itens` com `tipo: pergunta` e `responsavel: eu` (e `pai` = a história dos argumentos, se houver). Fique só com as de `situacao_pergunta: aberta`. Sem nenhuma, diga isso e pare.
2. **Entender cada uma.** `obter_processo` para saber as permissões da pessoa. Depois, `obter_item` de cada pergunta (descrição com contexto, opções e sugestão) e da história a que ela pertence (título e a seção `## Spec`, se houver). Quando a pergunta citar domínios ou ADRs e a pessoa puder ver a documentação, leia o trecho (`obter_dominio`, `obter_decisao`) para mostrar o que já está documentado.
3. **Mostrar tudo de uma vez**, agrupado por história, primeiro as que bloqueiam (campo **Bloqueia?** da descrição, conforme `shared/perguntas.md`):

   > **VO-41 · Pode cancelar depois que o restaurante aceitou?** (história VO-12, bloqueia)
   > Contexto: … · Opções: A) … B) … · **Sugestão:** B, porque … · O que o VO já diz: `dominio:Pedidos` › …

4. **Coletar as respostas** com `AskUserQuestion`: "aceito todas as sugestões", "aceito as sugestões, exceto algumas" ou "responder uma a uma". Para as exceções e para responder uma a uma, use uma pergunta por item, com as opções da pergunta e a sugestão marcada.
5. **Gravar**, com uma confirmação para o lote: mostre o texto exato de cada resposta (a opção escolhida e o porquê, em uma ou duas frases) e chame `responder_pergunta` em cada uma. Confira com `obter_item` que ficou `respondida`.
6. **Domínio.** Se uma resposta cria ou muda uma regra de negócio e a pessoa tem `criar` em documentação, ofereça propor a mudança no domínio (`propor_alteracao_dominio` com `item` = a história e a resposta como embasamento), conforme `shared/propostas.md`. Sem essa permissão, diga que a regra precisa ir para o domínio e que alguém com acesso à documentação deve propor.
7. **Devolver.** Liste as perguntas respondidas, as propostas criadas e, por história, o próximo passo: `/vo:refinar <chave>` para incorporar as respostas.

## O que grava

No VO: as respostas das perguntas e, se a pessoa aceitar, propostas de domínio.

## Não faz

- Mudar a spec da história: o `/vo:refinar` incorpora as respostas na próxima rodada.
- Responder perguntas atribuídas a outra pessoa, ou reabrir perguntas respondidas.
