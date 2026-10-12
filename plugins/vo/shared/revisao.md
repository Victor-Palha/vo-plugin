# Revisão: do diff ao comentário no VO

## Quais itens, qual base

- **Branch** = o `package` dos itens. Os itens do package são as histórias e sub-tasks com esse `package` (`listar_itens` sem filtro de tipo, filtrando pelo campo `package`).
- **Base** = a branch alvo da skill de processo (ex.: `dev`). Depois de `git fetch`, a comparação é contra `git merge-base HEAD origin/<base>`.
- **Diff** = `git diff <merge-base>`, com os arquivos novos registrados antes por `git add -N`. Os arquivos são `git diff --name-only <merge-base>` mais os de `git status --porcelain`.
- Com mudanças não commitadas, a revisão é **provisória**: serve para corrigir, mas não libera o PR.

## Apontamentos

- Todo apontamento tem `arquivo:linha` e cita a regra que o sustenta: `skill › Seção`, `Spec › R<n>`, `ADR-N`, `segurança: …` ou `correção: …`. **Sem citação, o apontamento cai**, e isso é dito na saída.
- Severidade: `bloqueia`, `importante` ou `sugestão`. A revisão é **limpa** quando não sobra `bloqueia` nem `importante` em aberto.
- Quem discorda de um apontamento é a pessoa. Registre `não se aplica: <motivo dela>`, **com as palavras dela**. Nunca invente o motivo.
- Se o mesmo `skill › Seção` é marcado "não se aplica" em mais de uma revisão (veja os comentários anteriores), sugira mudar a skill com `/vo:propor-skill`.

## Comentário de revisão (na história do package)

A primeira linha é fixa, porque o `/vo:preparar-pr` a procura:

```markdown
**Revisão VO** · `<sha curto do HEAD>` · <limpa | com apontamentos | provisória>

| # | Severidade | Onde | Regra | Situação |
| --- | --- | --- | --- | --- |
| A1 | bloqueia | `lib/x.ex:42` | `skill › Seção` | corrigido em `<sha>` · não se aplica: <motivo> · aberto |

**Cobertura da spec:** R1 ✓ (`test/x_test.exs`) · R2 ✓ · …
**Sugestões não aplicadas:** …
```

O `/vo:preparar-pr` só abre o PR se o comentário de revisão mais recente da história tiver o **sha igual ao HEAD** e o resultado **limpa**.
