---
name: configurar
description: Use ao começar a usar o plugin do VO num repositório, para trocar o projeto ou o quadro ligados a ele, ou quando outro comando /vo:* disser que falta a configuração. Testa a conexão com o View Office, liga o repositório a um projeto e quadro (.vo.json) e mostra o processo e as skills do projeto.
argument-hint: "[projeto] [prefixo do quadro]"
disable-model-invocation: true
allowed-tools: Bash(sh *scripts/execucao.sh*) Bash(sh *scripts/pre-condicoes.sh*) Bash(sh *scripts/regras.sh*)
---

# /vo:configurar

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/execucao.sh" configurar "${CLAUDE_SESSION_ID}" "$ARGUMENTS"`

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/pre-condicoes.sh" "${CLAUDE_PROJECT_DIR}" --sem-config`

Argumentos: `$ARGUMENTS` (opcional: o nome do projeto e o prefixo do quadro).

## Regras

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/regras.sh" transparencia`

## Antes de começar

As linhas do começo dizem se há repositório git (`git=`), a raiz dele (`repositorio=`) e se já existe configuração (`config=`, `projeto_id=`, `quadro=`).

- `git=fora-de-repositorio`: avise que `.vo.json` ficará na pasta atual e que o normal é rodar na raiz do repositório do projeto; pergunte se continua.
- `config=ok`: é uma reconfiguração. Mostre o projeto e o quadro atuais e pergunte o que trocar.

## Passos

1. **Conexão.** Chame a ferramenta `listar_projetos` do servidor `vo`.
   - Erro de token (401, "Invalid or missing API token"): oriente a criar um token em View Office → **Tokens de API** e a trocá-lo em `/plugin` › **Installed** › vo › **Configure options**. Pare.
   - Erro de assinatura (403): diga que o acesso da companhia está suspenso até a contratação de um plano em Configurações. Pare.
   - Nenhum projeto: diga que o token não alcança nenhum projeto (revise os projetos do token no VO). Pare.
2. **Projeto.** Use o dos argumentos se ele casar com um nome da lista. Senão, com um só projeto, use-o; com vários, pergunte (`AskUserQuestion`), mostrando as permissões de cada um.
3. **Quadro.** Chame `obter_projeto`. Com um só quadro, use-o; com vários, pergunte, ou use o prefixo dos argumentos.
4. **Processo.** Chame `obter_processo` e mostre, em poucas linhas:
   - as permissões da pessoa em `kanban`, `documentacao` e `skills`;
   - as colunas do quadro com a categoria de cada uma;
   - as skills de processo (nome e uma linha do que dizem) e quantas skills há de cada tipo.
5. **Gravar.** Mostre o conteúdo e confirme antes de gravar `<repositorio>/.vo.json` (com a ferramenta de escrita de arquivos):
   ```json
   {
     "projeto_id": "<id>",
     "projeto": "<nome>",
     "quadro": "<prefixo>"
   }
   ```
   Se o arquivo já existia, mostre o que muda. O arquivo não tem segredo: recomende versioná-lo, para o time usar a mesma configuração.

   Depois de gravar, **confira** que o arquivo existe e tem o conteúdo certo (leia-o). Se a gravação for negada ou falhar, diga isso com clareza e mostre o conteúdo para a pessoa criar o arquivo; nunca diga que gravou sem ter conferido.
6. **Próximo passo.**
   - Projeto sem skills: explique que os comandos funcionam, mas sem padrões do projeto; sugira registrar as primeiras com `/vo:propor-skill` (modo inicial, que analisa o código).
   - Sem skill de processo: diga que os comandos vão perguntar a branch base, os checks e as colunas, e sugira registrar isso como skill de processo.
   - Termine com os comandos disponíveis para começar: `/vo:escrever-historia`, `/vo:refinar`, `/vo:responder-perguntas`.

## O que grava

Só `.vo.json` no repositório. Nada no VO.

## Não faz

- Criar ou alterar token, projeto, quadro ou skill.
- Guardar o token: ele fica na configuração do plugin, no cofre do sistema.
