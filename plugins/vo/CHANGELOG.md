# Changelog

## 0.0.11 — 12/10/2026

- `/vo:metricas`: junta as métricas do servidor (`obter_metricas`) com as locais pelo id da execução; tabelas por execução, comando e item; observações só com o que os números mostram.
- `scripts/metricas.py`: tempo (total, máquina, esperando, subagentes, MCP), chamadas lentas e tokens por execução, lidos dos metadados do histórico do Claude Code, sem o texto das conversas.
- `execucao.sh` guarda o histórico de todas as execuções (`execucoes.jsonl`), não só a última de cada sessão.
- Execuções que só existem no servidor usam o comando, o item e o início que o VO devolve em `agrupar_por: execucao`, sem deduzir pelos números.

## 0.0.10 — 11/10/2026

- `/vo:propor-skill`: mudança com análise de impacto (skills, itens ligados, código), diff e embasamento; modo inicial que analisa o repositório e propõe o primeiro conjunto de skills com fontes reais.
- `/vo:aprovar`: decide as propostas uma a uma, com a escolha da pessoa, e explica como ligar "Pode aprovar propostas" no token.
- Hook: o motivo da permissão diz por que a chamada pede confirmação (exclusão, decisão de proposta), em vez da frase genérica de rastreio.

## 0.0.9 — 11/10/2026

- `/vo:revisar`: diff contra o merge-base da base do processo, agente `revisor` com as skills dos arquivos, apontamentos sem citação descartados, correção um a um com "não se aplica" no motivo da pessoa e comentário de revisão com o sha na história.
- `/vo:preparar-pr`: exige árvore limpa, sub-tasks feitas, checks verdes e revisão limpa no HEAD; push, PR criado ou editado, itens na coluna de revisão, relatório ligado aos itens e as propostas que serão aplicadas.
- Regras comuns: `shared/revisao.md`.

## 0.0.8 — 11/10/2026

- `/vo:implementar`: pré-condições (spec, dependências, impedimento, responsável), branch do package sem criar por conta própria, implementador → escritor-testes com as skills dos arquivos previstos e reais, checks, ciclo de revisão até ficar limpa e commit local sem push, com comentário no item.
- Agentes `implementador`, `escritor-testes` e `revisor` (só leitura).
- Os comandos sabem quem está conectado pelo `voce` de `obter_processo` (responsável de uma sub-task, quem aprovou uma spec), com alternativa por `listar_itens` (`responsavel: eu`) para VO sem `voce`.

## 0.0.7 — 11/10/2026

- `/vo:planejar`: com a spec aprovada, divide a história em sub-tasks verticais com arquivos previstos e skills, mostra o plano inteiro e cria package, sub-tasks, dependências e propostas de ADR e de skill; devolve a primeira sub-task pronta.
- Agente `planejador`, só de leitura.
- Regras de propostas: só referencie o que já existe; skill ou domínio ainda em proposta se cita no texto como `PROP-N`.

## 0.0.6 — 11/10/2026

- `/vo:refinar`: uma rodada por chamada, com a spec na descrição da história, triagem em lote, até 5 perguntas por rodada, propostas ligadas à história e aprovação registrada na spec e em comentário.
- Agente `refinador`, só de leitura.

## 0.0.5 — 11/10/2026

- `/vo:escrever-historia`: entrevista, confere glossário e domínios, procura parecidas, cria a história sob o épico e propõe domínio novo quando preciso.
- `/vo:responder-perguntas`: responde em lote as perguntas abertas atribuídas a você e oferece propor a mudança de domínio.
- Regras de transparência: lista vazia ou "não existe" pode ser falta de permissão; os comandos conferem `permissoes` antes de afirmar que algo não existe ou de propor.

## 0.0.4 — 11/10/2026

- `/vo:configurar`: testa a conexão, liga o repositório a um projeto e quadro (`.vo.json`) e mostra o processo e as skills do projeto.
- Skill de apoio `vo-fundamentos` e as regras comuns em `shared/` (transparência, skills do projeto, propostas, perguntas, formato da spec, estados do fluxo).
- `scripts/pre-condicoes.sh`: confere repositório, configuração e GitHub CLI antes de cada comando.
- A configuração do repositório fica em `.vo.json` na raiz (a pasta `.claude/` é protegida pelo Claude Code e recusava a gravação).
- As regras comuns entram nos comandos por `!` (`scripts/regras.sh`), sem depender de permissão de leitura fora do repositório; cada skill libera no `allowed-tools` só os scripts do plugin que chama (sem isso o `!` é bloqueado), e o `verificar.py` confere isso.
- Toda escrita é conferida depois de feita; uma gravação negada é relatada, nunca dada como feita.

## 0.0.3 — 11/10/2026

- Rastreio da execução: `scripts/execucao.sh` marca o começo de um comando e o hook `PreToolUse` anexa `_vo` (comando, execução, item) às chamadas ao VO, para as métricas por comando.
- Permissões durante um comando: leitura e criação/propostas aprovadas; `excluir_*`, `aprovar_proposta` e `rejeitar_proposta` sempre perguntam; fora de um comando (ou após 3 h parado) o hook não age.
- O hook roda em Python 3.9 (o do macOS); `scripts/testar_hook.py` cobre os casos e roda na CI.

## 0.0.2 — 11/10/2026

- O endereço do MCP passa a ser opcional: sem preencher, vale o padrão `https://vo.rivia-hub.tech/mcp`; só o token é obrigatório na instalação.

## 0.0.1 — 11/10/2026

- Estrutura do plugin: marketplace `rivia`, manifesto `vo` com a configuração do endereço do MCP e do token de API (sensível), e o servidor MCP do VO no `.mcp.json`.
- Verificação estrutural (`scripts/verificar.py`) e CI.
