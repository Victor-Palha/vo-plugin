# Perguntas

Pergunta boa é a que só uma pessoa pode responder. Antes de perguntar, procure a resposta nos domínios, nas ADRs, nas skills, nos itens ligados (`obter_vizinhanca`) e no código.

## Na conversa (entrevista)

- Uma pergunta por vez, com a ferramenta de pergunta (`AskUserQuestion`).
- Ofereça opções concretas e marque a recomendada, dizendo por quê.

## No refinamento (itens `pergunta` no VO)

- **No máximo 5 perguntas novas por rodada.** O que tiver resposta razoável vira **decisão padrão** na spec, que a pessoa aceita em lote, em vez de pergunta.
- Cada pergunta vira um item `pergunta` filho da história (`pai`), atribuído a quem decide (`responsavel`, por e-mail: PO para regra de negócio, tech lead para decisão técnica).
- Título: a pergunta, numa frase. Descrição:
  - **Contexto**: o que levou à pergunta, com referências (`VO-12`, `ADR-3`, `dominio:X`);
  - **Opções**: duas a quatro, com o efeito de cada uma;
  - **Sugestão**: a opção recomendada e por quê;
  - **Bloqueia?**: se a história para até a resposta.
- **Convergência**: da segunda rodada em diante, pergunte só o que as respostas ou as mudanças abriram. Não reabra pergunta respondida; se a resposta quebrou uma suposição, marque a suposição como `quebrada` na spec.
