# Changelog

## 0.0.4 — 11/10/2026

- `/vo:configurar`: testa a conexão, liga o repositório a um projeto e quadro (`.claude/vo.json`) e mostra o processo e as skills do projeto.
- Skill de apoio `vo-fundamentos` e as regras comuns em `shared/` (transparência, skills do projeto, propostas, perguntas, formato da spec, estados do fluxo).
- `scripts/pre-condicoes.sh`: confere repositório, configuração e GitHub CLI antes de cada comando.

## 0.0.3 — 11/10/2026

- Rastreio da execução: `scripts/execucao.sh` marca o começo de um comando e o hook `PreToolUse` anexa `_vo` (comando, execução, item) às chamadas ao VO, para as métricas por comando.
- Permissões durante um comando: leitura e criação/propostas aprovadas; `excluir_*`, `aprovar_proposta` e `rejeitar_proposta` sempre perguntam; fora de um comando (ou após 3 h parado) o hook não age.
- O hook roda em Python 3.9 (o do macOS); `scripts/testar_hook.py` cobre os casos e roda na CI.

## 0.0.2 — 11/10/2026

- O endereço do MCP passa a ser opcional: sem preencher, vale o padrão `https://vo.rivia-hub.tech/mcp`; só o token é obrigatório na instalação.

## 0.0.1 — 11/10/2026

- Estrutura do plugin: marketplace `rivia`, manifesto `vo` com a configuração do endereço do MCP e do token de API (sensível), e o servidor MCP do VO no `.mcp.json`.
- Verificação estrutural (`scripts/verificar.py`) e CI.
