# Propostas: documentação muda junto com o trabalho

Durante um comando, o plugin **não edita** domínios, skills nem ADRs diretamente. Ele **propõe**. Uma pessoa aprova no VO (ou no `/vo:aprovar`), e a mudança só vale quando o item ligado for **concluído**. Assim a documentação nunca descreve o que ainda não está em produção.

## Quando propor

| Situação | Ferramenta |
| --- | --- |
| Conceito ou regra de negócio nova | `propor_dominio` ou `propor_alteracao_dominio` |
| Regra de negócio que mudou | `propor_alteracao_dominio` |
| Decisão técnica (biblioteca, padrão, arquitetura) | `propor_decisao` (com `substitui` se trocar uma ADR) |
| Padrão de código que falta ou está errado | `propor_skill` ou `propor_alteracao_skill` |

## Como propor

- **Leia antes**: `obter_dominio` ou `obter_skill`, e `listar_propostas` do mesmo alvo. Se já existe uma proposta aberta para o mesmo alvo, ajuste-a com `atualizar_proposta` em vez de criar outra.
- **Ligue ao item** do trabalho (`item`). Sem item, a mudança vale assim que for aprovada.
- **Embasamento**: por que mudar e o que sustenta a mudança. Obrigatório para skills; escreva-o também para domínios e ADRs.
- **Referências**: o que sustenta, na forma que o VO entende: `ADR-3`, `VO-12`, `dominio:Pedidos`, `skill:nome`, caminhos de código (`lib/app/pedidos.ex`) e URLs.
- **Conteúdo inteiro**: numa alteração de domínio ou skill, mande o conteúdo completo como deve ficar, não um trecho.
- Mostre a proposta à pessoa antes de enviar (`shared/transparencia.md`). Depois, devolva a `PROP-N` e diga que ela vale quando o item for concluído, depois de aprovada.

## O que não fazer

- `atualizar_dominio` ou `atualizar_decisao` para mudanças que nascem do trabalho.
- Aprovar a própria proposta.
- Propor sem ter lido o estado atual do alvo.
