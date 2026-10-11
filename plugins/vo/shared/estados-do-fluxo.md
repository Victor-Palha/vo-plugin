# Estados do fluxo: comandos e colunas do quadro

Os nomes das colunas variam por quadro. O plugin usa a **categoria** de cada coluna (`pendente`, `em_andamento`, `concluido`, de `obter_processo`) e, quando houver, a skill de **processo** do projeto, que diz o papel de cada coluna.

| Momento | Coluna (pela skill de processo; sem ela, pela categoria) |
| --- | --- |
| História escrita (`/vo:escrever-historia`) | primeira coluna `pendente` (ex.: Backlog) |
| Em refinamento (`/vo:refinar`) | coluna de planejamento, se a skill de processo indicar; senão, não move |
| Implementação começou (`/vo:implementar`) | primeira coluna `em_andamento` (ex.: Em desenvolvimento) |
| PR aberto (`/vo:preparar-pr`) | coluna de revisão indicada pela skill de processo; sem ela, pergunte |
| Bloqueado por pergunta ou padrão que falta | coluna de impedimento, se existir |
| Em produção | primeira coluna `concluido`. É quando as propostas aprovadas do item são aplicadas |

Regras:

- Mover um item é escrita: mostre e confirme (`shared/transparencia.md`).
- Não mova para uma coluna `concluido` sem a pessoa pedir: isso aplica as propostas aprovadas ligadas ao item.
- Sem skill de processo e sem como decidir, pergunte uma vez qual coluna usar e sugira registrar o mapeamento com `/vo:propor-skill`.
