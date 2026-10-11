# Changelog

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
