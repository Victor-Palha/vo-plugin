# Skills do projeto: o conhecimento vem do VO

O plugin não traz regra de nenhum projeto. Arquitetura, padrões, processo e glossário estão nas **skills** do projeto, no VO.

## Começo de todo comando

Chame `obter_processo` com o `projeto_id` de `.claude/vo.json`. Ele traz:

- as **permissões** da pessoa em cada módulo (kanban, documentacao, skills);
- os **quadros** com as colunas e a categoria de cada uma: `pendente`, `em_andamento` ou `concluido`;
- as skills de **processo** completas: fluxo de branches, checks que precisam passar, o que cada coluna significa;
- o **índice** das demais skills (nome, quando usar, caminhos), sem o conteúdo.

Siga as skills de processo em vez de supor. Se o projeto não tiver nenhuma, pergunte à pessoa uma vez o que faltar (branch base, comando de checks) e sugira registrar isso com `/vo:propor-skill`.

## Antes de ler ou mudar arquivos

Chame `skills_para_arquivos` com os caminhos **relativos à raiz do repositório**:

- no planejamento, com os arquivos **previstos**;
- na implementação e na revisão, com os arquivos **reais** (`git diff --name-only <base>` e `git status --porcelain`).

A resposta traz cada skill com os arquivos que ela casou (ou `geral: true` para as que valem para tudo) e `sem_skill`, a lista de arquivos que nenhuma skill cobre.

- Siga as skills devolvidas. Quando delegar a um agente, **passe o conteúdo delas no prompt**: agentes não buscam skills sozinhos.
- Ao justificar uma escolha ou um apontamento, cite a regra como `nome-da-skill › Título da seção`.
- Arquivo em `sem_skill` não é erro. Se o mesmo tipo de arquivo aparecer sem padrão em vários trabalhos, sugira uma skill (`/vo:propor-skill`).

## Quando a skill e o código discordam

Não "conserte" a skill no código nem o código na skill em silêncio. Mostre a divergência à pessoa. Se a skill estiver desatualizada, proponha a alteração (`shared/propostas.md`); se o código estiver fora do padrão, trate como apontamento.
