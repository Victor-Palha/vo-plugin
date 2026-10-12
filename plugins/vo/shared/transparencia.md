# Transparência: o que sai da máquina passa pela pessoa

Toda escrita fora do repositório local é visível para o time e fica no histórico. Por isso:

1. **Planeje** todas as escritas do passo: itens, comentários, perguntas, propostas, movimentações, push, PR.
2. **Mostre** exatamente o que vai ser gravado: título, texto, destino (projeto, item, coluna, branch). Texto longo vai inteiro, em bloco.
3. **Confirme uma vez por lote** com a ferramenta de pergunta (`AskUserQuestion`), oferecendo "gravar tudo", "ajustar" e "cancelar". Não peça confirmação item por item.
4. **Execute** e **devolva as chaves e os links** do que foi criado (`VO-12`, `PROP-3`, URL do PR).
5. **Confira** o resultado de cada escrita. Se uma for negada ou falhar, diga isso com clareza; nunca relate como feito o que não foi conferido.

Regras:

- Ler no VO, no git e no GitHub é livre; só a escrita precisa de confirmação.
- Fale com o VO **só pelas ferramentas do servidor do plugin** (`mcp__plugin_vo_vo__*`), que passam pelo rastreio e pelas confirmações do plugin. Se elas não existirem e houver outro servidor do VO na sessão (um configurado à mão, por exemplo), não use o outro: pare e explique que o Claude Code esconde o servidor do plugin quando há um servidor manual com o mesmo endereço. A pessoa remove o manual (`claude mcp remove <nome>`, na pasta do projeto) e abre a sessão de novo.
- O VO só mostra o que a pessoa pode ver: lista vazia ou "não existe" pode ser falta de permissão. Antes de afirmar que algo não existe, confira `permissoes` em `obter_processo`. Sem `visualizar` num módulo, diga que não tem acesso a ele; sem `criar`, não proponha nada nele.
- Se uma ferramenta falhar, mostre a mensagem do VO e pare o lote. Não tente contornar permissões nem repetir às cegas.
- Nunca aprove nem rejeite propostas por conta própria. `aprovar_proposta` e `rejeitar_proposta` só no `/vo:aprovar`, com a pessoa decidindo cada uma.
- Nunca peça, mostre nem grave tokens, senhas ou valores de secrets. O VO só entrega o nome dos secrets.
- Ao terminar, diga o que ficou feito, o que ficou pendente e o próximo comando que faz sentido.
