---
name: escrever-historia
description: Use quando alguém quiser registrar uma história nova no View Office a partir de uma ideia, de um pedido ou de um épico. Entrevista uma pergunta por vez, confere o glossário e os domínios do projeto, procura histórias parecidas, escreve a história em linguagem de negócio e cria a task sob o épico, propondo um domínio novo quando aparece um conceito novo.
argument-hint: "[ideia, ou chave do épico]"
disable-model-invocation: true
allowed-tools: Bash(sh *scripts/execucao.sh*) Bash(sh *scripts/pre-condicoes.sh*) Bash(sh *scripts/regras.sh*)
---

# /vo:escrever-historia

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/execucao.sh" escrever-historia "${CLAUDE_SESSION_ID}" "$ARGUMENTS"`

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/pre-condicoes.sh" "${CLAUDE_PROJECT_DIR}"`

Argumentos: `$ARGUMENTS` (a ideia em texto livre, a chave de um épico, ou nada).

Se a última linha acima for `situacao=bloqueado` com `config=ausente`, diga que o repositório ainda não está ligado a um projeto do VO e peça para rodar `/vo:configurar`. Pare.

## Regras

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/regras.sh" transparencia perguntas propostas`

## O que é uma boa história aqui

- **Uma ação de uma pessoa usuária**, com valor claro. Se a ideia tiver várias ações, proponha várias histórias.
- **Linguagem de negócio, com os termos do glossário do projeto.** Sem rotas, tabelas, nomes de módulo ou detalhes de implementação; isso é do refinamento e do planejamento.
- **Critérios de aceite verificáveis**, do ponto de vista de quem usa.

## Passos

1. **Contexto do projeto.** Com o `projeto_id` e o `quadro` das linhas acima:
   - `obter_processo`: colunas e skills. Leia com `obter_skill` as skills do tipo `glossario`, se houver.
   - `listar_dominios`: os conceitos de negócio já documentados.
   - **Épico**: se os argumentos trazem uma chave, `obter_item` dela (precisa ser um `epico`). Senão, liste os épicos abertos (`listar_itens` com `tipo: epico`, ignorando os que estão em coluna `concluido`) e pergunte em qual a história entra, com a opção "nenhum".
2. **Entrevista**, uma pergunta por vez (`AskUserQuestion`), até ficar claro:
   - **quem** usa (a persona, com o nome que o glossário dá);
   - **o que** a pessoa quer fazer (uma ação);
   - **por quê** (o valor);
   - as **regras** já conhecidas e o que está **fora do escopo**.

   Não pergunte o que os domínios já respondem; use o que está lá e mostre a fonte. Se a pessoa usar um termo que não está no glossário nem nos domínios, pergunte se é um conceito novo ou outro nome para um existente.
3. **Parecidas.** Busque histórias com os termos principais (`listar_itens` com `busca`, mais de uma busca se preciso). Se houver parecidas em aberto, mostre-as e pergunte: seguir mesmo assim, ligar a nova como relacionada, ou desistir.
4. **Escrever.** Título no infinitivo, começando pela ação (ex.: "Cancelar um pedido até 5 minutos depois da compra"). Descrição:

   ```markdown
   **Como** <persona>, **quero** <ação> **para** <valor>.

   ### Contexto
   <de onde veio a necessidade; termos e regras de domínio envolvidos, com `dominio:Nome`>

   ### Critérios de aceite
   - [ ] <comportamento observável>

   ### Fora do escopo
   - <o que não entra nesta história>
   ```

   Mostre a história inteira e ajuste com a pessoa até ela aprovar.
5. **Gravar**, com uma confirmação para o lote (`shared/transparencia.md`):
   - `criar_item` com `tipo: task`, `pai` (o épico, se houver), título, descrição e prioridade (pergunte; o padrão é `media`). Não atribua responsável: isso fica para o refinamento.
   - `criar_ligacao` com `de` = a história e `para` = `dominio:<Nome>`, para cada domínio envolvido (`tipo: implementa`, com um contexto de uma linha dizendo qual regra a história toca).
   - Se a pessoa escolheu ligar a uma história parecida: `criar_ligacao` de uma para a outra, com `tipo: relacionado` e o contexto da semelhança.
   - Conceito novo, ou regra de negócio nova: proponha (`propor_dominio` ou `propor_alteracao_dominio`, com `item` = a nova história e o embasamento da entrevista), conforme `shared/propostas.md`.
6. **Conferir e devolver.** `obter_item` da história criada para confirmar título, épico e ligações. Mostre a chave (`VO-…`), as propostas criadas (`PROP-…`) e sugira o próximo passo: `/vo:refinar <chave>`.

## O que grava

No VO: a história (task), as ligações dela e, quando houver, propostas de domínio. Nada no repositório.

## Não faz

- Refinar regras em detalhe, abrir itens `pergunta` ou estimar: isso é o `/vo:refinar`.
- Criar épicos (peça para criar no VO, se faltar) ou mover a história de coluna.
- Editar domínios diretamente: só propõe.
