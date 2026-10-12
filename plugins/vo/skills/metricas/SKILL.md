---
name: metricas
description: Use para ver como o plugin do VO está sendo usado: tempo, tokens, chamadas e erros por execução de comando, juntando as métricas locais desta máquina (histórico do Claude Code, sem o texto das conversas) com as do servidor do VO, e apontando só o que os números mostram.
argument-hint: "[item ou comando] [dias]"
disable-model-invocation: true
allowed-tools: Bash(sh *scripts/execucao.sh*) Bash(sh *scripts/pre-condicoes.sh*) Bash(python3 *scripts/metricas.py*)
---

# /vo:metricas

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/execucao.sh" metricas "${CLAUDE_SESSION_ID}" "$ARGUMENTS"`

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/pre-condicoes.sh" "${CLAUDE_PROJECT_DIR}"`

Argumentos: `$ARGUMENTS` (opcionais: uma chave de item, o nome de um comando e o número de dias; padrão 30).

## Métricas locais (desta máquina)

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/metricas.py" --json --limite 30 "$ARGUMENTS"`

O JSON acima vem de `scripts/metricas.py`. Ele lê o histórico do Claude Code desta máquina, mas só os metadados: horários, tokens, nomes de ferramenta e ids. **O texto das conversas não é lido nem mostrado.** Por execução, ele traz:
- os minutos: total, máquina, esperando a pessoa, subagentes e MCP;
- as chamadas MCP e as lentas;
- os tokens: entrada, cache, saída e total;
- os agentes usados.

Uma execução vai do início do comando até o início do próximo comando na mesma sessão.

## Privacidade

- Os números locais ficam nesta conversa. Não os grave no VO nem em arquivo, a menos que a pessoa peça.
- Nunca leia os transcripts do Claude Code diretamente. Só o script os lê, e só os metadados.

## Passos

1. **Servidor.** Se `.vo.json` existir (`config=ok` acima), chame `obter_metricas` com o `projeto_id`, os mesmos `dias` (e `comando` ou `item`, se houver) e `agrupar_por: ["execucao", "comando", "item"]`. Sem `.vo.json`, mostre só as locais e diga que o lado do servidor precisa de `/vo:configurar`. O filtro de item no servidor vale por chamada; o local, pelo item dos argumentos do comando.
2. **Juntar pelo id da execução**:
   - **as duas fontes**: tempo e tokens do lado local, chamadas, erros e p95 do servidor. As chamadas MCP locais e as do servidor devem bater; se não baterem, diga quanto difere;
   - **só local**: execução de outro projeto, ou sem chamadas ao VO;
   - **só servidor**: antes de concluir, confira se ela é desta máquina, porque o filtro de item local só vê o item dos argumentos. Rode `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/metricas.py" --json --execucoes <id>,<id>` com os ids que só o servidor trouxe; as que voltarem entram como "as duas". As restantes são de outra pessoa ou de outra máquina, sem tempo nem tokens. O comando, o item e o início vêm do grupo `execucao` do servidor; se o VO não os trouxer, escreva "desconhecido". Nunca deduza o comando pelos números.
3. **Mostrar**:
   - **por execução**, das mais recentes para as mais antigas: comando, item, início, minutos (total, máquina, esperando), subagentes, chamadas, erros, p95 e tokens (saída e total);
   - **por comando**: execuções, mediana de minutos e de tokens, e a taxa de erro do servidor;
   - **por item**: as execuções de cada comando. Para itens refinados, as rodadas e as perguntas (`obter_item` e a tabela **Rodadas** da spec; `listar_itens` com `tipo: pergunta` e `pai`, abertas e respondidas).
4. **Observações**, só o que os números mostram, cada uma com o número que a sustenta:
   - refinamento com mais de 3 rodadas, ou rodada com 5 perguntas, que é o limite;
   - MCP lento: chamadas locais lentas, ou p95 do servidor acima de 1 s;
   - erros acima de 5% das chamadas de um comando, com as ferramentas que falharam;
   - mais da metade do tempo esperando a pessoa;
   - execução com mais do que o dobro da mediana de tokens do mesmo comando;
   - divergência entre as chamadas locais e as do servidor. Compare só sem filtro de item: com ele, o servidor conta apenas as chamadas sobre o item.

   Sem nada disso, diga que os números não mostram problema. Não dê conselho que os números não sustentam.

## O que grava

Nada.
