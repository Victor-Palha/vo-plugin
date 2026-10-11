# Changelog

## 0.0.2 — 11/10/2026

- O endereço do MCP passa a ser opcional: sem preencher, vale o padrão `https://vo.rivia-hub.tech/mcp`; só o token é obrigatório na instalação.

## 0.0.1 — 11/10/2026

- Estrutura do plugin: marketplace `rivia`, manifesto `vo` com a configuração do endereço do MCP e do token de API (sensível), e o servidor MCP do VO no `.mcp.json`.
- Verificação estrutural (`scripts/verificar.py`) e CI.
