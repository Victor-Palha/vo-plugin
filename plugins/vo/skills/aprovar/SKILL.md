---
name: aprovar
description: Use para decidir as propostas abertas no View Office (skills, domínios e ADRs) que você pode aprovar. Mostra cada proposta com o diff, o embasamento e as referências e aprova ou rejeita uma a uma, com uma confirmação explícita para cada decisão. Exige a permissão de aprovar e um token com "Pode aprovar propostas".
argument-hint: "[PROP-N]"
disable-model-invocation: true
allowed-tools: Bash(sh *scripts/execucao.sh*) Bash(sh *scripts/pre-condicoes.sh*) Bash(sh *scripts/regras.sh*)
---

# /vo:aprovar

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/execucao.sh" aprovar "${CLAUDE_SESSION_ID}" "$ARGUMENTS"`

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/pre-condicoes.sh" "${CLAUDE_PROJECT_DIR}"`

Argumentos: `$ARGUMENTS` (opcional: uma proposta, `PROP-N`).

Se a última linha acima for `situacao=bloqueado` com `config=ausente`, peça para rodar `/vo:configurar` e pare.

## Regras

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/regras.sh" transparencia propostas`

## Quem decide é a pessoa

Aqui, e só aqui, o plugin chama `aprovar_proposta` e `rejeitar_proposta`, e sempre depois de a pessoa escolher a decisão daquela proposta. Nunca decida em lote, nunca sugira a decisão como se já estivesse tomada e nunca escreva o motivo de uma rejeição por ela.

## Passos

1. **Pode decidir?** `obter_processo`: quem é você e as permissões. Decidir pede `aprovar` no módulo da proposta: `skills` para skill, `documentacao` para domínio e ADR. Sem `aprovar` em nenhum módulo, diga que um administrador concede essa permissão em **Permissões** e pare.
2. **Fila.** `listar_propostas` (as abertas, que já incluem as `aprovada` e as `conflito`). Fique com as que você pode decidir: `aberta` e `conflito`, no módulo em que você tem `aprovar`. Com `PROP-N` nos argumentos, só ela. Sem nenhuma, diga isso e pare. Mostre a fila: chave, alvo, operação, título, quem propôs, item e situação. As que você mesmo propôs vêm marcadas.
3. **Uma de cada vez.** `obter_proposta` e mostre:
   - o alvo, a operação, a versão de base e se ela ficou **desatualizada** (e o que mudou desde então);
   - o **diff** do conteúdo e dos campos;
   - o **embasamento** e as referências;
   - o **item** ligado e quando a mudança vale: sem item, ou com o item já concluído, vale na aprovação; senão, quando o item for concluído;
   - se foi você que propôs.
4. **A decisão é da pessoa.** Pergunte com `AskUserQuestion`; sem essa ferramenta, pergunte no chat. Vale só uma resposta explícita da pessoa sobre esta proposta ("aprovar", "rejeitar: <motivo>", "pular"); na dúvida, pergunte de novo. As opções:
   - **aprovar**, com um comentário opcional;
   - **aprovar e aplicar já**: só para proposta com item ainda aberto, quando a pessoa quer que a mudança valha antes da conclusão;
   - **rejeitar**: peça o motivo e use as palavras da pessoa;
   - **pular**.

   Para proposta em `conflito`, as opções são **aplicar mesmo assim** (`forcar: true`, sobre a versão atual), **rejeitar** e **pular**. Proposta desatualizada: avise que aprovar pode dar conflito e sugira pedir a quem propôs para rebasear (`atualizar_proposta` com `rebasear`).
5. **Executar** a decisão: `aprovar_proposta` (com `comentario`, `aplicar_agora` ou `forcar`, conforme a escolha) ou `rejeitar_proposta` (com `motivo`). Confira com `obter_proposta` (situação, quem decidiu e, se aplicada, a versão nova do alvo) e siga para a próxima.
   - **Erro de token** ("Este token não pode aprovar nem rejeitar propostas"): explique que o token do plugin precisa ter **Pode aprovar propostas**. Para isso, crie um token novo com a opção marcada em **Tokens**, no VO, e troque o `vo_token` do plugin em `/plugin` › **Installed** › vo › **Configure options**. Até lá, decida pela tela de Propostas do VO. Pare a fila.
6. **Resumo.** As propostas aprovadas (e as aplicadas já), as rejeitadas com o motivo, as puladas e as que esperam a conclusão de um item, com a chave do item.

## O que grava

No VO: só as decisões que a pessoa escolheu, uma por proposta.

## Não faz

- Decidir sem a escolha explícita da pessoa, ou várias propostas com uma resposta só.
- Editar o conteúdo de uma proposta. Para isso existe `atualizar_proposta`, que é de quem propôs e derruba a aprovação.
