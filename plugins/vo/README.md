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

## Skills de apoio

- `vo-fundamentos`: como o VO organiza projetos, quadros, itens, documentação, grafo, skills, propostas e métricas, e onde fica cada artefato do fluxo. O Claude carrega quando trabalha com as ferramentas do VO.

## Agentes

- `refinador` (só leitura): usado pelo `/vo:refinar`. Lê domínios, ADRs, skills, propostas e código e devolve a spec da rodada, as perguntas candidatas, as decisões padrão e a documentação a propor. Quem grava é o comando, depois de mostrar.
- `planejador` (só leitura): usado pelo `/vo:planejar`. Lê código, skills, domínios e ADRs e devolve as sub-tasks verticais com arquivos previstos, skills, testes, dependências, cobertura das regras e as ADRs e skills a propor.

## Hooks

- `PreToolUse` nas ferramentas do MCP do VO (`scripts/injetar_execucao.py`): durante um comando, anexa a execução às chamadas para as métricas e decide a permissão (exclusões e decisões de proposta perguntam; o resto é aprovado). A execução é marcada no começo de cada comando por `scripts/execucao.sh`.

## Regras comuns (`shared/`)

- `transparencia.md`: o que sai da máquina passa pela pessoa (planejar, mostrar, confirmar, executar, devolver links).
- `skills-do-projeto.md`: `obter_processo` no começo e `skills_para_arquivos` antes de mexer em arquivos.
- `propostas.md`: quando e como propor mudanças em domínios, ADRs e skills.
- `perguntas.md`: uma por vez na conversa; no refinamento, até 5 por rodada como itens `pergunta`.
- `formato-da-spec.md`: a seção `## Spec` na descrição da história.
- `estados-do-fluxo.md`: em que coluna cada etapa deixa o item.

## Scripts

- `scripts/execucao.sh`: marca o começo de um comando (rastreio da execução).
- `scripts/pre-condicoes.sh`: confere repositório, configuração e GitHub CLI antes de cada comando.
