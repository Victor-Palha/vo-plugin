#!/usr/bin/env python3
"""
Testa o rastreio da execução (VO-114): `execucao.sh` grava a execução da
sessão e o hook `injetar_execucao.py` anexa `_vo` e decide a permissão.

    python3 scripts/testar_hook.py

Roda em Python 3.9 (o `python3` do macOS), como o hook na máquina de quem
instala o plugin.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SCRIPTS = RAIZ / "plugins" / "vo" / "scripts"


def hook(cache: str, sessao: str, ferramenta: str) -> dict | None:
    entrada = {
        "session_id": sessao,
        "tool_name": f"mcp__plugin_vo_vo__{ferramenta}",
        "tool_input": {"projeto_id": "p1"},
    }
    saida = subprocess.run(
        [sys.executable, str(SCRIPTS / "injetar_execucao.py")],
        input=json.dumps(entrada), capture_output=True, text=True, check=True,
        env={**os.environ, "XDG_CACHE_HOME": cache},
    ).stdout
    return json.loads(saida)["hookSpecificOutput"] if saida.strip() else None


def main() -> int:
    falhas = []

    def conferir(condicao: bool, mensagem: str) -> None:
        if not condicao:
            falhas.append(mensagem)

    with tempfile.TemporaryDirectory() as cache:
        env = {**os.environ, "XDG_CACHE_HOME": cache}

        conferir(hook(cache, "s1", "listar_projetos") is None, "sem execução, o hook deveria ficar mudo")

        saida = subprocess.run(
            ["sh", str(SCRIPTS / "execucao.sh"), "refinar", "s1", "detalhar vo-12 e VO-13"],
            capture_output=True, text=True, check=True, env=env,
        ).stdout
        conferir(saida.startswith("execucao="), f"execucao.sh deveria imprimir execucao=…, imprimiu {saida!r}")

        for ferramenta, esperada in [
            ("listar_projetos", "allow"),
            ("propor_skill", "allow"),
            ("criar_item", "allow"),
            ("excluir_item", "ask"),
            ("excluir_ligacao", "ask"),
            ("aprovar_proposta", "ask"),
            ("rejeitar_proposta", "ask"),
        ]:
            resultado = hook(cache, "s1", ferramenta)
            if resultado is None:
                falhas.append(f"{ferramenta}: o hook não respondeu")
                continue
            conferir(resultado["permissionDecision"] == esperada, f"{ferramenta}: decisão {resultado['permissionDecision']}, esperada {esperada}")
            vo = resultado["updatedInput"].get("_vo", {})
            conferir(vo.get("comando") == "refinar" and vo.get("item") == "VO-12", f"{ferramenta}: _vo inesperado {vo}")
            conferir(resultado["updatedInput"].get("projeto_id") == "p1", f"{ferramenta}: os argumentos originais se perderam")

        conferir(hook(cache, "outra-sessao", "listar_projetos") is None, "outra sessão não deveria ser marcada")

        arquivo = Path(cache) / "vo-plugin" / "execucoes" / "s1.json"
        velho = time.time() - 4 * 3600
        os.utime(arquivo, (velho, velho))
        conferir(hook(cache, "s1", "listar_projetos") is None, "execução parada há 4 h deveria ter expirado")

    if falhas:
        print("testar_hook.py falhou:")
        for falha in falhas:
            print(f"  - {falha}")
        return 1

    print("ok: rastreio da execução e decisões de permissão")
    return 0


if __name__ == "__main__":
    sys.exit(main())
