# vo

Plugin do View Office para o Claude Code. Visão geral, instalação e configuração estão no [README do repositório](../../README.md).

## Comandos

Ainda nenhum: os comandos chegam nas próximas versões.

## Skills de apoio

Nenhuma ainda.

## Agentes

Nenhum ainda.

## Hooks

- `PreToolUse` nas ferramentas do MCP do VO (`scripts/injetar_execucao.py`): durante um comando, anexa a execução às chamadas para as métricas e decide a permissão (exclusões e decisões de proposta perguntam; o resto é aprovado). A execução é marcada no começo de cada comando por `scripts/execucao.sh`.

## Regras comuns (`shared/`)

Nenhuma ainda.
