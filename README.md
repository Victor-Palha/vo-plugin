# Plugin do View Office para o Claude Code

Trabalhe no [View Office](https://vo.rivia-hub.tech) (VO) direto do Claude Code: escrever e refinar histórias, responder perguntas, planejar, implementar, revisar e preparar o PR, com o **conhecimento do seu projeto vindo do VO**.

O plugin não traz regras de nenhum projeto. Arquitetura, padrões, fluxo de branches, checks e glossário ficam nas **Skills** do projeto, dentro do VO, versionadas e alteradas só por proposta aprovada. O plugin carrega as skills que valem para os arquivos em que está trabalhando. Quando o trabalho pede uma mudança de domínio, uma ADR ou uma skill, ele **propõe**, e a mudança só vale quando o item for concluído.

Tudo o que o plugin produz fica no VO: a spec na descrição do item, as dúvidas como itens `pergunta`, o plano como sub-tasks e package, a revisão e o relatório final. Nada fica em arquivo local, a não ser `.vo.json`, que liga o repositório ao projeto.

## Requisitos

- Claude Code.
- Uma conta no View Office com acesso a um projeto, e um **token de API** (View Office → Tokens de API).
- `git` e `gh` (GitHub CLI) autenticados, para implementar e abrir PRs.

## Instalação

```
/plugin marketplace add Victor-Palha/vo-plugin
/plugin install vo@rivia
```

Na instalação, o Claude Code pede o **token de API** (guardado no cofre de credenciais do sistema) e o endereço do MCP. O padrão é `https://vo.rivia-hub.tech/mcp`; troque só se usar outra instalação do VO. Para mudar depois: `/plugin configure vo`.

Em seguida, dentro do repositório do projeto:

```
/vo:configurar
```

## Permissões e métricas

Cada comando `/vo:*` marca as chamadas que faz ao VO com o comando e a execução, para a aba **Métricas** do projeto (e o `/vo:metricas`) mostrarem o uso por comando. Isso é feito por um hook `PreToolUse` que só age durante um comando do plugin. Para marcar a chamada, o Claude Code exige que o hook decida a permissão:

- chamadas que leem ou criam/propõem no VO são **aprovadas** durante o comando (os comandos já mostram e pedem confirmação antes de gravar);
- **exclusões** (`excluir_*`) e **decisões de proposta** (`aprovar_proposta`, `rejeitar_proposta`) **sempre perguntam**;
- fora de um comando, ou numa execução parada há mais de 3 horas, o hook não faz nada e vale a permissão normal do Claude Code.

O hook precisa de `python3` (3.9 ou mais novo; o do macOS serve). O VO nunca guarda o conteúdo das chamadas, só a ferramenta, o comando, a duração e se deu erro.

## Comandos

Os comandos estão em construção. A lista completa, com o que cada um faz, está em [plugins/vo/README.md](plugins/vo/README.md).

## Estrutura

```
.claude-plugin/marketplace.json   marketplace "rivia"
plugins/vo/
  .claude-plugin/plugin.json      manifesto, versão e configuração (endereço e token)
  .mcp.json                       servidor MCP do VO
  skills/<comando>/SKILL.md       comandos (/vo:...) e skills de apoio
  agents/                         agentes usados pelos comandos
  shared/                         regras comuns aos comandos
  hooks/                          hooks do plugin
  scripts/                        scripts usados pelos comandos e hooks
  CHANGELOG.md
scripts/verificar.py              verificação estrutural (CI)
```

## Contribuindo

- Toda mudança em `plugins/` sobe a versão em `plugin.json` (semver) e ganha uma seção no `CHANGELOG.md`.
- O header `X-VO-Cliente` do `.mcp.json` leva a mesma versão.
- Antes do PR: `python3 scripts/verificar.py --base origin/main`, `python3 scripts/testar_hook.py`, `python3 scripts/testar_metricas.py` e `claude plugin validate plugins/vo --strict`. A CI roda todos (os testes de scripts em Python 3.9).

## Licença

MIT.
