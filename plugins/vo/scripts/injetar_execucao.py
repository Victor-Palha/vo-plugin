#!/usr/bin/env python3
"""
Hook PreToolUse das ferramentas do MCP do VO (VO-114).

Durante um comando do plugin (`execucao.sh` gravou a execução da sessão),
anexa o argumento reservado `_vo` = {comando, execucao, item} a cada chamada
ao VO, para as métricas saberem de qual comando e execução ela veio (o VO
remove `_vo` antes de a ferramenta ver os argumentos).

Para alterar a entrada, o Claude Code exige que o hook decida a permissão:
  - exclusões (`excluir_*`) e decisões de proposta (`aprovar_proposta`,
    `rejeitar_proposta`) sempre perguntam;
  - as demais (leitura, criação, propostas) são aprovadas, porque os
    comandos já mostram e pedem confirmação antes de gravar.

Fora de um comando (sem execução da sessão, ou parada há mais de 3 horas),
o hook não faz nada e vale a permissão normal do Claude Code.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

VALIDADE_S = 3 * 3600
SEMPRE_PERGUNTAR = {"aprovar_proposta", "rejeitar_proposta"}


def ferramenta(nome_completo: str) -> str:
    """`mcp__plugin_vo_vo__excluir_item` → `excluir_item`."""
    return nome_completo.rsplit("__", 1)[-1]


def decisao(nome: str) -> str:
    if nome.startswith("excluir_") or nome in SEMPRE_PERGUNTAR:
        return "ask"
    return "allow"


def execucao_da_sessao(sessao: str) -> dict | None:
    cache = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    arquivo = cache / "vo-plugin" / "execucoes" / f"{sessao}.json"
    try:
        if time.time() - arquivo.stat().st_mtime > VALIDADE_S:
            return None
        dados = json.loads(arquivo.read_text())
        arquivo.touch()  # a execução segue ativa enquanto houver chamadas
        return dados
    except (OSError, json.JSONDecodeError):
        return None


def main() -> None:
    try:
        entrada = json.load(sys.stdin)
    except json.JSONDecodeError:
        return

    execucao = execucao_da_sessao(entrada.get("session_id") or "")
    if not execucao:
        return

    nome = ferramenta(entrada.get("tool_name", ""))
    argumentos = dict(entrada.get("tool_input") or {})
    argumentos["_vo"] = {k: v for k, v in execucao.items() if v}

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decisao(nome),
                "permissionDecisionReason": f"/vo:{execucao.get('comando')}: chamada ao VO marcada com a execução.",
                "updatedInput": argumentos,
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
