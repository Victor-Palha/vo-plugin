# vo

Plugin do View Office para o Claude Code. Visão geral, instalação e configuração estão no [README do repositório](../../README.md).

## Comandos

| Comando | O que faz |
| --- | --- |
| `/vo:configurar` | Testa a conexão com o VO, liga o repositório a um projeto e quadro (`.vo.json`) e mostra o processo e as skills do projeto. |
| `/vo:escrever-historia` | Entrevista uma pergunta por vez, confere glossário e domínios, procura histórias parecidas e cria a história (task) sob o épico, propondo domínio novo quando aparece um conceito novo. |
| `/vo:responder-perguntas` | Mostra as perguntas abertas atribuídas a você, com contexto, opções e sugestão; aceita respostas em lote, grava e oferece propor a mudança de domínio. |
| `/vo:refinar <história>` | Uma rodada de refinamento por chamada: lê o que mudou, monta a spec com o agente `refinador`, faz a triagem em lote, abre até 5 perguntas, propõe a documentação ligada à história e registra a aprovação. |
| `/vo:planejar <história>` | Divide a história com spec aprovada em sub-tasks verticais com o agente `planejador` (arquivos previstos e skills de cada uma) e, com uma confirmação, cria o package, as sub-tasks, as dependências e as propostas de ADR e de skill. |
| `/vo:implementar <sub-task>` | Confere spec, dependências e impedimentos, entra na branch do package, orquestra `implementador` e `escritor-testes` com as skills dos arquivos, roda os checks, revisa com o `revisor` até ficar limpo e faz o commit local, comentando no item. |
| `/vo:revisar [item]` | Revisa a branch contra a base com o agente `revisor`; cada apontamento cita a regra que o sustenta. Corrige um apontamento por vez, registra discordâncias com o motivo da pessoa e grava o resultado na história, com o sha. |
| `/vo:preparar-pr [história]` | Com a revisão limpa no HEAD e os checks verdes, faz o push, cria ou edita o PR para a base do processo, move os itens para revisão, registra o relatório e lista as propostas que serão aplicadas na conclusão. |
| `/vo:propor-skill [mudança\|inicial]` | Cria ou muda uma skill do projeto por proposta, com análise de impacto, diff e embasamento. Num projeto sem skills, o modo inicial analisa o repositório e propõe o primeiro conjunto, com fontes reais. |
| `/vo:aprovar [PROP-N]` | Mostra cada proposta que você pode decidir (diff, embasamento, referências, quando vale) e aprova ou rejeita uma a uma, com a decisão escolhida pela pessoa. Exige o token com "Pode aprovar propostas". |
| `/vo:metricas [item\|comando] [dias]` | Junta as métricas locais desta máquina (tempo e tokens por execução, lidos do histórico do Claude Code sem o texto das conversas) com as do servidor (chamadas, erros, p95), pelo id da execução, e aponta só o que os números mostram. |

## Skills de apoio

- `vo-fundamentos`: como o VO organiza projetos, quadros, itens, documentação, grafo, skills, propostas e métricas, e onde fica cada artefato do fluxo. O Claude carrega quando trabalha com as ferramentas do VO.

## Agentes

- `refinador` (só leitura): usado pelo `/vo:refinar`. Lê domínios, ADRs, skills, propostas e código e devolve a spec da rodada, as perguntas candidatas, as decisões padrão e a documentação a propor. Quem grava é o comando, depois de mostrar.
- `planejador` (só leitura): usado pelo `/vo:planejar`. Lê código, skills, domínios e ADRs e devolve as sub-tasks verticais com arquivos previstos, skills, testes, dependências, cobertura das regras e as ADRs e skills a propor.
- `implementador`: usado pelo `/vo:implementar`. Escreve o código de produção da sub-task seguindo as skills recebidas e devolve arquivos, decisões, dúvidas e padrões que faltam. Não escreve testes nem faz commit.
- `escritor-testes`: usado pelo `/vo:implementar`. Escreve um teste por cenário da spec, roda a suíte e devolve o mapa cenário → teste. Não muda código de produção: bug vira apontamento.
- `revisor` (só leitura): usado pelo `/vo:implementar` e pelo `/vo:revisar`. Revisa o diff contra a base; cada apontamento cita a regra que o sustenta (skill › seção, regra da spec, ADR, segurança ou correção) e vem com a cobertura da spec e um veredito.

## Hooks

- `PreToolUse` nas ferramentas do MCP do VO (`scripts/injetar_execucao.py`): durante um comando, anexa a execução às chamadas para as métricas e decide a permissão (exclusões e decisões de proposta perguntam; o resto é aprovado). A execução é marcada no começo de cada comando por `scripts/execucao.sh`.

## Regras comuns (`shared/`)

- `transparencia.md`: o que sai da máquina passa pela pessoa (planejar, mostrar, confirmar, executar, devolver links).
- `skills-do-projeto.md`: `obter_processo` no começo e `skills_para_arquivos` antes de mexer em arquivos.
- `propostas.md`: quando e como propor mudanças em domínios, ADRs e skills.
- `perguntas.md`: uma por vez na conversa; no refinamento, até 5 por rodada como itens `pergunta`.
- `formato-da-spec.md`: a seção `## Spec` na descrição da história.
- `revisao.md`: base, diff, apontamentos citados e o comentário de revisão que o `/vo:preparar-pr` confere.
- `estados-do-fluxo.md`: em que coluna cada etapa deixa o item.

## Scripts

- `scripts/execucao.sh`: marca o começo de um comando (rastreio da execução).
- `scripts/pre-condicoes.sh`: confere repositório, configuração e GitHub CLI antes de cada comando.
- `scripts/regras.sh`: imprime as regras comuns de `shared/` que cada comando pede.
- `scripts/metricas.py`: métricas locais por execução (tempo, chamadas MCP, tokens), lidas só dos metadados do histórico do Claude Code.
- `scripts/injetar_execucao.py`: o hook que anexa a execução às chamadas ao VO e decide a permissão.
