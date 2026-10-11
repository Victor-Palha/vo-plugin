# Transparência: o que sai da máquina passa pela pessoa

Toda escrita fora do repositório local é visível para o time e fica no histórico. Por isso:

1. **Planeje** todas as escritas do passo: itens, comentários, perguntas, propostas, movimentações, push, PR.
2. **Mostre** exatamente o que vai ser gravado: título, texto, destino (projeto, item, coluna, branch). Texto longo vai inteiro, em bloco.
3. **Confirme uma vez por lote** com a ferramenta de pergunta (`AskUserQuestion`), oferecendo "gravar tudo", "ajustar" e "cancelar". Não peça confirmação item por item.
4. **Execute** e **devolva as chaves e os links** do que foi criado (`VO-12`, `PROP-3`, URL do PR).

Regras:

- Ler no VO, no git e no GitHub é livre; só a escrita precisa de confirmação.
- Se uma ferramenta falhar, mostre a mensagem do VO e pare o lote. Não tente contornar permissões nem repetir às cegas.
- Nunca aprove nem rejeite propostas por conta própria. `aprovar_proposta` e `rejeitar_proposta` só no `/vo:aprovar`, com a pessoa decidindo cada uma.
- Nunca peça, mostre nem grave tokens, senhas ou valores de secrets. O VO só entrega o nome dos secrets.
- Ao terminar, diga o que ficou feito, o que ficou pendente e o próximo comando que faz sentido.
