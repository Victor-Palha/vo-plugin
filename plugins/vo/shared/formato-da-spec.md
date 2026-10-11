# Formato da spec

A spec fica na **descrição do item** da história, abaixo do texto original da história. O refinamento reescreve só a seção `## Spec`; o que está acima dela não muda.

```markdown
<texto original da história>

## Spec

**Estado:** rascunho · aguardando · pronta · aprovada
**Aprovada por:** <nome> em <AAAA-MM-DD>   (só quando aprovada)

### Objetivo
Uma ou duas frases: o que a pessoa usuária consegue fazer ao final.

### Regras
| # | Regra | Origem |
| --- | --- | --- |
| R1 | … | `dominio:Pedidos`, `ADR-3`, `skill:nome › Seção`, resposta de `VO-40`, código `lib/x.ex`, ou **suposição S1** |

### Cenários
- **R1 · caminho feliz**: Dado …, quando …, então ….
- **R1 · erro**: …

### Suposições
| # | Suposição | Situação |
| --- | --- | --- |
| S1 | … | aberta · confirmada · quebrada |

### Decisões padrão
| # | Decisão | Situação |
| --- | --- | --- |
| D1 | … | proposta · aceita · alterada · encaminhada (`VO-41`) |

### Fora do escopo
- …

### Rodadas
| Rodada | Data | Perguntas | O que mudou |
| --- | --- | --- | --- |
| 1 | AAAA-MM-DD | `VO-40`, `VO-41` | … |
```

Regras:

- Toda regra tem **origem**. Regra sem origem é suposição (`S<n>`) ou vira pergunta.
- Os números (`R`, `S`, `D`) não mudam entre rodadas; regra removida fica riscada (`~~R3~~`), não renumerada.
- **Estados**: `rascunho` enquanto a primeira rodada não termina; `aguardando` com pergunta bloqueante aberta; `pronta` sem pendência; `aprovada` depois que a pessoa responsável aprova. Só spec `aprovada` vai para o planejamento.
