#!/usr/bin/env python3
"""
Testa plugins/vo/scripts/metricas.py com um histórico sintético: tokens sem
contar duas vezes a mesma mensagem, espera da pessoa, duração das chamadas
MCP e dos subagentes, a janela de cada execução e, principalmente, que o
texto das conversas nunca aparece na saída.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "plugins" / "vo" / "scripts" / "metricas.py"
SEGREDO = "TEXTO-SECRETO-DA-CONVERSA"


def escrever(caminho: Path, linhas: list[dict]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("".join(json.dumps(l) + "\n" for l in linhas), encoding="utf-8")


def ts(segundos: int) -> str:
    return f"2026-10-11T10:{segundos // 60:02d}:{segundos % 60:02d}.000Z"


def assistente(segundos: int, mid: str, blocos: list[dict], saida: int = 10) -> dict:
    return {
        "type": "assistant", "timestamp": ts(segundos),
        "message": {"id": mid, "role": "assistant", "content": blocos,
                    "usage": {"input_tokens": 5, "output_tokens": saida,
                              "cache_read_input_tokens": 100, "cache_creation_input_tokens": 20}},
    }


def resultado(segundos: int, tool_id: str) -> dict:
    return {"type": "user", "timestamp": ts(segundos), "toolUseResult": {},
            "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_id, "content": SEGREDO}]}}


def pessoa(segundos: int) -> dict:
    return {"type": "user", "timestamp": ts(segundos), "message": {"role": "user", "content": SEGREDO}}


def main() -> int:
    falhas = []

    def conferir(condicao: bool, mensagem: str) -> None:
        if not condicao:
            falhas.append(mensagem)

    with tempfile.TemporaryDirectory() as raiz:
        raiz = Path(raiz)
        cache, config = raiz / "cache", raiz / "config"
        escrever(cache / "vo-plugin" / "execucoes.jsonl", [
            {"sessao": "s1", "comando": "refinar", "execucao": "e1", "item": "APP-1", "inicio": ts(0).replace(".000", "")},
            {"sessao": "s1", "comando": "planejar", "execucao": "e2", "item": "APP-1", "inicio": ts(600).replace(".000", "")},
        ])
        sessao = config / "projects" / "-repo" / "s1.jsonl"
        escrever(sessao, [
            pessoa(0),
            {"type": "user", "isMeta": True, "timestamp": ts(0), "message": {"role": "user", "content": [{"type": "text", "text": SEGREDO}]}},
            # a mesma mensagem em duas linhas (pensamento + ferramenta): conta uma vez
            assistente(10, "m1", [{"type": "thinking", "thinking": SEGREDO}]),
            assistente(11, "m1", [{"type": "tool_use", "id": "t1", "name": "mcp__plugin_vo_vo__obter_item", "input": {"x": SEGREDO}}]),
            resultado(14, "t1"),  # 3 s de MCP: lenta com --lenta-ms 2000
            assistente(20, "m2", [{"type": "tool_use", "id": "t2", "name": "Agent", "input": {"prompt": SEGREDO}}]),
            resultado(80, "t2"),  # 60 s de subagente
            assistente(90, "m3", [{"type": "text", "text": SEGREDO}]),
            {"type": "queue-operation", "timestamp": ts(209)},
            pessoa(210),  # esperou 120 s desde a última atividade (90 s)
            assistente(220, "m4", [{"type": "text", "text": SEGREDO}]),
            # já é a próxima execução: fora da janela de e1
            pessoa(600),
            assistente(610, "m5", [{"type": "text", "text": SEGREDO}], saida=999),
        ])
        agentes = sessao.parent / "s1" / "subagents"
        escrever(agentes / "agent-a.jsonl", [
            assistente(30, "a1", [{"type": "tool_use", "id": "t3", "name": "mcp__plugin_vo_vo__obter_skill", "input": {}}], saida=7),
            resultado(31, "t3"),
            assistente(70, "a2", [{"type": "text", "text": SEGREDO}], saida=3),
        ])
        (agentes / "agent-a.meta.json").write_text(json.dumps({"agentType": "vo:refinador", "toolUseId": "t2"}))

        env = {**os.environ, "XDG_CACHE_HOME": str(cache), "CLAUDE_CONFIG_DIR": str(config)}
        rodar = lambda *args: subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--dias", "100000"],
            capture_output=True, text=True, check=True, env=env).stdout

        saida = rodar("--json")
        conferir(SEGREDO not in saida, "o texto da conversa vazou na saída JSON")
        conferir(SEGREDO not in rodar(), "o texto da conversa vazou na tabela")

        execucoes = {e["execucao"]: e for e in json.loads(saida)["execucoes"]}
        e1 = execucoes.get("e1")
        conferir(e1 is not None and "e2" in execucoes, f"execuções esperadas e1 e e2, vieram {list(execucoes)}")
        if e1:
            conferir(e1["tokens"]["saida"] == 10 + 10 + 10 + 10 + 7 + 3,
                     f"tokens de saída {e1['tokens']['saida']}: m1 contou duas vezes ou m5 entrou na janela")
            conferir(e1["minutos"]["total"] == round(220 / 60, 1), f"total {e1['minutos']['total']}")
            conferir(e1["minutos"]["esperando"] == 2.0, f"esperando {e1['minutos']['esperando']}, esperado 2.0")
            conferir(e1["minutos"]["subagentes"] == 1.0, f"subagentes {e1['minutos']['subagentes']}")
            conferir(e1["mcp"]["chamadas"] == 2, f"chamadas MCP {e1['mcp']['chamadas']} (principal + subagente)")
            conferir(e1["mcp"]["lentas"] == [{"ferramenta": "obter_item", "ms": 3000}], f"lentas {e1['mcp']['lentas']}")
            conferir([a["tipo"] for a in e1["agentes"]] == ["vo:refinador"], f"agentes {e1['agentes']}")

        filtrada = json.loads(subprocess.run(
            [sys.executable, str(SCRIPT), "planejar", "APP-1", "--json", "--dias", "100000"],
            capture_output=True, text=True, check=True, env=env).stdout)
        conferir([e["execucao"] for e in filtrada["execucoes"]] == ["e2"], "filtro por comando e item")

        por_id = json.loads(subprocess.run(
            [sys.executable, str(SCRIPT), "planejar", "--execucoes", "e1,nao-existe", "--json"],
            capture_output=True, text=True, check=True, env=env).stdout)
        conferir([e["execucao"] for e in por_id["execucoes"]] == ["e1"], "--execucoes deveria ignorar os outros filtros")

    if falhas:
        print("testar_metricas.py falhou:")
        for falha in falhas:
            print(f"  - {falha}")
        return 1
    print("ok: métricas locais sem texto das conversas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
