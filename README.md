# Plugin do View Office para o Claude Code

Trabalhe no [View Office](https://vo.rivia-hub.tech) (VO) direto do Claude Code: escrever e refinar histórias, responder perguntas, planejar, implementar, revisar e preparar o PR, com o **conhecimento do seu projeto vindo do VO**.

O plugin não traz regras de nenhum projeto. Arquitetura, padrões, fluxo de branches, checks e glossário ficam nas **Skills** do projeto, dentro do VO, versionadas e alteradas só por proposta aprovada. O plugin carrega as skills que valem para os arquivos em que está trabalhando. Quando o trabalho pede uma mudança de domínio, uma ADR ou uma skill, ele **propõe**, e a mudança só vale quando o item for concluído.

Tudo o que o plugin produz fica no VO: a spec na descrição do item, as dúvidas como itens `pergunta`, o plano como sub-tasks e package, a revisão e o relatório final. Nada fica em arquivo local, a não ser `.vo.json`, que liga o repositório ao projeto.

## Requisitos

- Claude Code.
- Uma conta no View Office com acesso a um projeto e um **token de API**, criado em View Office → Tokens de API. O token age com as suas permissões no projeto. Para decidir propostas pelo `/vo:aprovar`, marque **Pode aprovar propostas** ao criá-lo.
- `git` e `gh` (GitHub CLI) autenticados, para implementar e abrir PRs.
- `python3` 3.9 ou mais novo (o do macOS serve), usado pelo hook e pelas métricas locais.

## Instalação

```
/plugin marketplace add Victor-Palha/vo-plugin
/plugin install vo@rivia
```

Na instalação, o Claude Code pede o **token de API** (guardado no cofre de credenciais do sistema) e o endereço do MCP. O padrão é `https://vo.rivia-hub.tech/mcp`; troque só se usar outra instalação do VO. Para mudar depois: `/plugin` › **Installed** › vo › **Configure options**.

Se você já tinha o MCP do VO configurado à mão (por exemplo, com `claude mcp add`), remova-o na pasta do projeto: `claude mcp remove <nome>`. Quando há um servidor manual com o mesmo endereço, o Claude Code esconde o do plugin, e as chamadas ficam fora do rastreio e das confirmações do plugin.

Em seguida, dentro do repositório do projeto:

```
/vo:configurar
```

Ele testa a conexão, liga o repositório a um projeto e quadro do VO (`.vo.json`, para versionar) e mostra o processo e as skills do projeto. Num projeto ainda sem skills, comece por `/vo:propor-skill inicial`: ele lê o repositório e propõe o primeiro conjunto, que alguém com permissão aprova com `/vo:aprovar`.

## Fluxo

```
/vo:escrever-historia   → história no épico, com domínios e propostas
/vo:refinar <história>  ↔ /vo:responder-perguntas   (rodadas até a spec ficar aprovada)
/vo:planejar <história> → sub-tasks, package e dependências
/vo:implementar <sub>   → branch, código, testes, checks, revisão e commit local
/vo:revisar             → revisão do package, comentário com o sha
/vo:preparar-pr         → push, PR, itens em revisão e relatório
/vo:metricas            → tempo, tokens e chamadas por execução
```

Cada comando mostra o que vai gravar no VO, no git ou no GitHub e pede uma confirmação por lote. As propostas de domínio, ADR e skill só passam a valer depois de aprovadas, e as ligadas a um item só quando ele chega à coluna concluída.

## Permissões e métricas

Cada comando `/vo:*` marca as chamadas que faz ao VO com o comando e a execução, para a aba **Métricas** do projeto (e o `/vo:metricas`) mostrarem o uso por comando. Isso é feito por um hook `PreToolUse` que só age durante um comando do plugin. Para marcar a chamada, o Claude Code exige que o hook decida a permissão:

- chamadas que leem ou criam/propõem no VO são **aprovadas** durante o comando (os comandos já mostram e pedem confirmação antes de gravar);
- **exclusões** (`excluir_*`) e **decisões de proposta** (`aprovar_proposta`, `rejeitar_proposta`) **sempre perguntam**;
- fora de um comando, ou numa execução parada há mais de 3 horas, o hook não faz nada e vale a permissão normal do Claude Code.

O hook precisa de `python3` (3.9 ou mais novo; o do macOS serve). O VO nunca guarda o conteúdo das chamadas, só a ferramenta, o comando, a duração e se deu erro.

## Comandos

A lista completa, com o que cada comando, agente e script faz, está em [plugins/vo/README.md](plugins/vo/README.md).

## Privacidade

- O token fica no cofre de credenciais do sistema, nunca em arquivo.
- O VO registra de cada chamada só a ferramenta, o comando, a duração e se deu erro, nunca os argumentos.
- O `/vo:metricas` lê do histórico local do Claude Code só metadados (horários, tokens, nomes de ferramenta), nunca o texto das conversas.

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
