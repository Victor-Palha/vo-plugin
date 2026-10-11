---
name: implementar
description: Use para implementar uma sub-task do View Office no repositório. Confere spec, dependências, impedimentos e responsável, entra na branch do package conforme a skill de processo, move o item para desenvolvimento, orquestra os agentes implementador e escritor-testes com as skills dos arquivos, roda os checks do projeto, revisa e corrige até a revisão ficar limpa e faz o commit local, sem push, comentando o resultado no item.
argument-hint: "<chave da sub-task>"
disable-model-invocation: true
allowed-tools: Bash(sh *scripts/execucao.sh*) Bash(sh *scripts/pre-condicoes.sh*) Bash(sh *scripts/regras.sh*)
---

# /vo:implementar

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/execucao.sh" implementar "${CLAUDE_SESSION_ID}" "$ARGUMENTS"`

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/pre-condicoes.sh" "${CLAUDE_PROJECT_DIR}" --git`

Argumentos: `$ARGUMENTS` (a chave da sub-task).

Se a última linha acima for `situacao=bloqueado`, diga o que falta (`config=ausente`: rodar `/vo:configurar`; `git=fora-de-repositorio` ou `git=ausente`: rodar dentro do repositório do projeto, com o git instalado) e pare.

## Regras

!`sh "${CLAUDE_PLUGIN_ROOT}/scripts/regras.sh" transparencia skills-do-projeto propostas perguntas estados-do-fluxo`

## Git: o que pode e o que não pode

- Pode: `status`, `diff`, `log`, `fetch`, `switch`, `pull --ff-only`, `add` dos arquivos da sub-task, `add -N` e `commit`.
- Nunca: `push`, `reset --hard`, `checkout -- .`, `restore` de arquivos que não são da sub-task, `clean`, `rebase`, `stash drop`, `--force` em qualquer comando. O push é do `/vo:preparar-pr`.
- A lista de arquivos alterados vem **sempre** de `git status --porcelain`, nunca da memória da conversa.

## Passos

1. **Qual sub-task.** `obter_item` da chave. Precisa ser `subtask`. Uma `task` com sub-tasks: pergunte qual. Uma `task` sem sub-tasks: sugira `/vo:planejar`.
2. **Pré-condições** (só leitura):
   - **Spec**: a história (`pai`) precisa estar com a spec `aprovada`. Senão, pare e sugira `/vo:refinar`.
   - **Coluna**: numa coluna `concluido`, pare.
   - **Responsável**: compare com `voce` de `obter_processo` (`shared/skills-do-projeto.md`). Se for outra pessoa, pare, a menos que a pessoa diga que vai assumir. Sem responsável, ela vai ser atribuída a você no passo 4.
   - **Dependências** (ligações `depende de`): cada uma precisa estar implementada, seja numa coluna depois do desenvolvimento, seja `concluido`, seja com commits na branch (`git log --oneline --grep <chave>`). Se faltar alguma, mostre e recomende começar por ela.
   - **Impedimento**: se a sub-task está na coluna de impedimento, ou a seção **Impedimento** cita uma `PROP-N` que ainda não está `aplicada` (`obter_proposta`), pare e diga quem precisa aprovar o quê.
   - **Checks**: os da skill de processo; sem eles, os da seção **Checks** da sub-task; sem nenhum, pergunte uma vez.
   - **Base e branch**: a base vem da skill de processo, e a branch é o `package` da sub-task. Sem package, pare e sugira `/vo:planejar`.
3. **Onde o repositório está.** `git status --porcelain` e `git branch --show-current`:
   - **Na branch do package, com mudanças ou commits desta sub-task**: é uma **retomada**. Mostre o que já existe (`git status`, `git log <base>..HEAD --oneline`) e continue do passo que falta, sem refazer.
   - **Com mudanças em outra branch**: pare. Peça para a pessoa guardar ou commitar antes. Não mexa nos arquivos dela.
   - **Limpo**: `git fetch`. Se a branch do package existe (local ou no remoto), `git switch <package>` e, se ela segue o remoto, `git pull --ff-only`. Se não existe, **não crie por conta própria**: proponha criá-la a partir de `origin/<base>` no lote do passo 4.
4. **Começar**, com uma confirmação para o lote:
   - atribuir a sub-task a você (`atualizar_item` com `responsavel: eu`), se estiver sem responsável;
   - mover para a coluna de desenvolvimento (`shared/estados-do-fluxo.md`);
   - criar a branch (`git switch --no-track -c <package> origin/<base>`, sem seguir a base: o upstream é definido no push do `/vo:preparar-pr`), se for o caso.

   Confira com `obter_item` e `git branch --show-current`.
5. **Skills previstas.** `skills_para_arquivos` com os **Arquivos previstos** da sub-task. Guarde o conteúdo de cada skill devolvida.
6. **Implementador.** Chame o agente `implementador` deste plugin (`vo:implementador`) com a sub-task inteira, as regras e os cenários que ela cobre (da spec), o conteúdo das skills, os checks e, numa retomada, o que já existe.
7. **Skills reais.** `git status --porcelain`. Chame `skills_para_arquivos` com os arquivos reais e junte as skills novas às do passo 5.
8. **Testes.** Chame o agente `escritor-testes` (`vo:escritor-testes`) com os cenários, a seção **Testes** da sub-task, o relatório do implementador, os arquivos reais e as skills. Se ele achar bugs, devolva-os ao `implementador` e rode os testes de novo (até 2 vezes).
9. **Checks.** Rode os checks do projeto. Se falharem, mande a saída ao `implementador` (até 3 tentativas). Se continuarem falhando, pare: relate a falha com a saída, deixe as mudanças sem commit e comente no item o que falta.
10. **Revisão.** Registre os arquivos novos com `git add -N <arquivos>` e gere `git diff origin/<base>`. Chame o agente `revisor` (`vo:revisor`) com o diff, os arquivos, a spec, a sub-task e as skills. Depois:
    - **Apontamentos `bloqueia` ou `importante`**: os de código vão ao `implementador`; os de teste ou cobertura vão ao `escritor-testes`. Rode os checks e revise de novo, passando os apontamentos anteriores. São no máximo 3 rodadas. Se ainda sobrar apontamento, pare e mostre.
    - **Sugestões**: mostre à pessoa, sem ciclo.

    O ciclo termina com veredito `limpa` e checks verdes.
11. **Dúvidas e padrões** (dos relatórios dos agentes):
    - **Dúvida de regra de negócio**: mostre o que foi assumido. A pessoa aceita a suposição, que fica registrada no comentário, ou abre uma pergunta. A pergunta é um item `pergunta` filho da história, para quem decide, conforme `shared/perguntas.md`. Com a pergunta aberta, a sub-task vai para a coluna de impedimento e o commit espera a resposta.
    - **Padrão que falta**: ofereça `propor_skill` sem `item`, conforme `shared/propostas.md`.
12. **Fechar**, com uma confirmação para o lote:
    - **commit local**: `git add` dos arquivos de `git status --porcelain`, com a mensagem no formato da skill de processo. Sem formato definido, use o padrão do `git log` do repositório. A mensagem termina com a chave da sub-task;
    - **comentário na sub-task** (`comentar_item`):
      - o que foi feito;
      - as regras cobertas, com os testes;
      - os checks;
      - o veredito da revisão, com as sugestões não aplicadas;
      - o commit (hash curto);
      - as suposições aceitas e as propostas;
    - as perguntas, as propostas e a ida para impedimento do passo 11, se houver.

    Confira com `git log -1 --stat` e `obter_item`.
13. **Devolver.** O commit, o comentário e o próximo passo:
    - a próxima sub-task pronta do package (`listar_itens` com `pai` = a história; sem dependência pendente e sem impedimento): `/vo:implementar <chave>`;
    - todas implementadas: `/vo:revisar` e depois `/vo:preparar-pr`.

## O que grava

No repositório: o código, os testes e um commit local na branch do package. No VO: o responsável, a coluna, o comentário e, quando houver, perguntas e propostas de skill.

## Não faz

- `git push`, abrir PR ou mover para revisão: isso é o `/vo:preparar-pr`.
- Mudar a spec ou o plano. Um furo na spec vira pergunta; um plano que não fecha, uma nota para `/vo:planejar`.
- Implementar mais de uma sub-task por vez.
