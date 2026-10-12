#!/usr/bin/env python3
"""
Métricas locais das execuções do plugin do VO (VO-122).

Para cada execução de um comando /vo:* registrada por `execucao.sh`, lê o
histórico do Claude Code desta máquina (`~/.claude/projects/*/<sessão>.jsonl`
e os transcripts dos subagentes da sessão) e calcula tempo e tokens.

Usa só metadados: horários, tipos de mensagem, nomes de ferramenta, ids e
contagens de tokens. Nunca usa nem exporta o texto das conversas, nem os
argumentos ou resultados das ferramentas.

  python3 metricas.py [filtros...] [--dias N] [--json] [--limite N] [--lenta-ms N]
  python3 metricas.py --execucoes <id>,<id> [--json]

Filtros soltos (o que o /vo:metricas recebe em $ARGUMENTS): uma chave de item
(APP-12), um número (dias) ou o nome de um comando (refinar). Uma execução
vai do seu início até o início da próxima execução na mesma sessão.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PREFIXO_MCP = "mcp__plugin_vo_vo__"
FERRAMENTAS_AGENTE = {"Agent", "Task"}
FERRAMENTAS_ESPERA = {"AskUserQuestion"}
CHAVE = re.compile(r"^[A-Za-z][A-Za-z0-9]*-\d+$")
ID_EXECUCAO = re.compile(r"^(\d{8}T\d{6}Z)-")


def cache_dir() -> Path:
    return Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "vo-plugin"


def projetos_dir() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"


def instante(texto: str | None) -> datetime | None:
    if not texto:
        return None
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        return None


def ler_jsonl(caminho: Path):
    try:
        with caminho.open(encoding="utf-8") as arquivo:
            for linha in arquivo:
                try:
                    yield json.loads(linha)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


## Execuções


def execucoes_registradas() -> list[dict]:
    """O histórico de `execucao.sh` e, para execuções anteriores a ele, o
    arquivo da sessão (só a última), com o início tirado do id."""
    vistas: dict[str, dict] = {}
    for linha in ler_jsonl(cache_dir() / "execucoes.jsonl"):
        if linha.get("execucao") and linha.get("sessao"):
            vistas[linha["execucao"]] = linha

    for arquivo in (cache_dir() / "execucoes").glob("*.json"):
        try:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        execucao = dados.get("execucao", "")
        casou = ID_EXECUCAO.match(execucao)
        if casou and execucao not in vistas:
            inicio = datetime.strptime(casou.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            vistas[execucao] = {**dados, "sessao": arquivo.stem, "inicio": inicio.isoformat()}

    execucoes = []
    for dados in vistas.values():
        inicio = instante(dados.get("inicio"))
        if inicio:
            execucoes.append({**dados, "inicio": inicio})
    execucoes.sort(key=lambda e: e["inicio"])
    return execucoes


def com_janelas(execucoes: list[dict]) -> list[dict]:
    """Cada execução termina quando começa a próxima da mesma sessão."""
    proxima: dict[str, datetime] = {}
    for execucao in reversed(execucoes):
        execucao["ate"] = proxima.get(execucao["sessao"])
        proxima[execucao["sessao"]] = execucao["inicio"]
    return execucoes


## Transcripts (só metadados)


def blocos(evento: dict) -> list[dict]:
    conteudo = (evento.get("message") or {}).get("content")
    return [b for b in conteudo if isinstance(b, dict)] if isinstance(conteudo, list) else []


def mensagem_da_pessoa(evento: dict) -> bool:
    if evento.get("type") != "user" or evento.get("isMeta") or evento.get("isSidechain"):
        return False
    if evento.get("toolUseResult") is not None:
        return False
    conteudo = (evento.get("message") or {}).get("content")
    if isinstance(conteudo, str):
        return True
    return bool(conteudo) and all(b.get("type") != "tool_result" for b in blocos(evento))


class Contagem:
    """Tokens (sem contar duas vezes a mesma mensagem) e duração das ferramentas."""

    def __init__(self, lenta_ms: int) -> None:
        self.lenta_ms = lenta_ms
        self.mensagens: set[str] = set()
        self.tokens = {"entrada": 0, "cache_leitura": 0, "cache_escrita": 0, "saida": 0}
        self.abertas: dict[str, tuple[str, datetime]] = {}
        self.mcp_chamadas = 0
        self.mcp_s = 0.0
        self.lentas: list[dict] = []
        self.agentes_s = 0.0
        self.espera_s = 0.0
        self.agentes_ids: set[str] = set()

    def evento(self, evento: dict, quando: datetime) -> None:
        mensagem = evento.get("message") or {}
        if evento.get("type") == "assistant":
            uso = mensagem.get("usage") or {}
            mid = mensagem.get("id")
            if uso and mid and mid not in self.mensagens:
                self.mensagens.add(mid)
                self.tokens["entrada"] += uso.get("input_tokens") or 0
                self.tokens["cache_leitura"] += uso.get("cache_read_input_tokens") or 0
                self.tokens["cache_escrita"] += uso.get("cache_creation_input_tokens") or 0
                self.tokens["saida"] += uso.get("output_tokens") or 0
            for bloco in blocos(evento):
                if bloco.get("type") == "tool_use" and bloco.get("id"):
                    self.abertas[bloco["id"]] = (bloco.get("name") or "", quando)
                    if bloco.get("name") in FERRAMENTAS_AGENTE:
                        self.agentes_ids.add(bloco["id"])
        elif evento.get("type") == "user":
            for bloco in blocos(evento):
                if bloco.get("type") != "tool_result":
                    continue
                nome, inicio = self.abertas.pop(bloco.get("tool_use_id"), ("", None))
                if not inicio:
                    continue
                segundos = max((quando - inicio).total_seconds(), 0.0)
                if nome.startswith(PREFIXO_MCP):
                    self.mcp_chamadas += 1
                    self.mcp_s += segundos
                    if segundos * 1000 >= self.lenta_ms:
                        self.lentas.append({"ferramenta": nome[len(PREFIXO_MCP):], "ms": round(segundos * 1000)})
                elif nome in FERRAMENTAS_AGENTE:
                    self.agentes_s += segundos
                elif nome in FERRAMENTAS_ESPERA:
                    self.espera_s += segundos

    def somar(self, outra: "Contagem") -> None:
        for chave, valor in outra.tokens.items():
            self.tokens[chave] += valor
        self.mcp_chamadas += outra.mcp_chamadas
        self.mcp_s += outra.mcp_s
        self.lentas += outra.lentas


def transcript(sessao: str) -> Path | None:
    return next(iter(sorted(projetos_dir().glob(f"*/{sessao}.jsonl"))), None)


def dentro(quando: datetime | None, inicio: datetime, ate: datetime | None) -> bool:
    return bool(quando) and quando >= inicio and (ate is None or quando < ate)


def medir(execucao: dict, lenta_ms: int) -> dict:
    inicio, ate = execucao["inicio"], execucao.get("ate")
    contagem = Contagem(lenta_ms)
    caminho = transcript(execucao["sessao"])
    ultimo = atividade = None
    pessoa_falou = False

    for evento in ler_jsonl(caminho) if caminho else []:
        quando = instante(evento.get("timestamp"))
        if not dentro(quando, inicio, ate):
            continue
        if mensagem_da_pessoa(evento):
            # A primeira é o próprio comando; as seguintes são respostas. A
            # espera conta da última atividade do modelo (não dos eventos de
            # fila que a retomada da sessão grava logo antes da mensagem).
            if pessoa_falou and atividade:
                contagem.espera_s += max((quando - atividade).total_seconds(), 0.0)
            pessoa_falou = True
            atividade = quando
        elif evento.get("type") in ("assistant", "user"):
            atividade = quando
        contagem.evento(evento, quando)
        ultimo = max(ultimo, quando) if ultimo else quando

    agentes = []
    if caminho:
        for meta in sorted((caminho.parent / execucao["sessao"] / "subagents").glob("*.meta.json")):
            try:
                dados = json.loads(meta.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if dados.get("toolUseId") not in contagem.agentes_ids:
                continue
            do_agente = Contagem(lenta_ms)
            horarios = []
            for evento in ler_jsonl(meta.with_name(meta.name.replace(".meta.json", ".jsonl"))):
                quando = instante(evento.get("timestamp"))
                if quando:
                    horarios.append(quando)
                    do_agente.evento(evento, quando)
            contagem.somar(do_agente)
            agentes.append({
                "tipo": dados.get("agentType") or "?",
                "minutos": round((max(horarios) - min(horarios)).total_seconds() / 60, 1) if horarios else 0.0,
                "tokens_saida": do_agente.tokens["saida"],
                "tokens_total": sum(do_agente.tokens.values()),
            })

    total_s = (ultimo - inicio).total_seconds() if ultimo else 0.0
    espera_s = min(contagem.espera_s, total_s)
    return {
        "execucao": execucao["execucao"],
        "comando": execucao.get("comando") or "",
        "item": execucao.get("item") or "",
        "sessao": execucao["sessao"],
        "inicio": inicio.isoformat().replace("+00:00", "Z"),
        "transcript": bool(caminho),
        "minutos": {
            "total": round(total_s / 60, 1),
            "maquina": round((total_s - espera_s) / 60, 1),
            "esperando": round(espera_s / 60, 1),
            "subagentes": round(contagem.agentes_s / 60, 1),
            "mcp": round(contagem.mcp_s / 60, 1),
        },
        "mcp": {"chamadas": contagem.mcp_chamadas, "lentas": contagem.lentas},
        "tokens": {**contagem.tokens, "total": sum(contagem.tokens.values())},
        "agentes": agentes,
    }


## Saída


def filtros_soltos(valores: list[str]) -> dict:
    filtros: dict = {}
    for valor in " ".join(valores).split():
        if CHAVE.match(valor):
            filtros["item"] = valor.upper()
        elif valor.isdigit():
            filtros["dias"] = int(valor)
        elif valor:
            filtros["comando"] = valor.lower().removeprefix("/vo:")
    return filtros


def tabela(resultado: list[dict]) -> str:
    linhas = [
        "| Execução | Comando | Item | Início (UTC) | Min total | Máquina | Esperando | Subagentes | MCP (min) | Chamadas MCP | Lentas | Tokens saída | Tokens total |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in resultado:
        m = r["minutos"]
        linhas.append(
            f"| {r['execucao']} | {r['comando']} | {r['item'] or '-'} | {r['inicio'][:16].replace('T', ' ')} "
            f"| {m['total']} | {m['maquina']} | {m['esperando']} | {m['subagentes']} | {m['mcp']} "
            f"| {r['mcp']['chamadas']} | {len(r['mcp']['lentas'])} | {r['tokens']['saida']} | {r['tokens']['total']} |"
        )
    return "\n".join(linhas)


def main() -> int:
    parser = argparse.ArgumentParser(description="Métricas locais das execuções do plugin do VO.")
    parser.add_argument("filtros", nargs="*", help="chave de item, número de dias ou nome do comando")
    parser.add_argument("--dias", type=int)
    parser.add_argument("--json", action="store_true", help="saída em JSON")
    parser.add_argument("--limite", type=int, default=50, help="as N execuções mais recentes (padrão 50)")
    parser.add_argument("--lenta-ms", type=int, default=2000, help="chamada MCP lenta a partir de (padrão 2000 ms)")
    parser.add_argument("--execucoes", default="", help="só estes ids de execução, separados por vírgula (ignora os outros filtros)")
    args = parser.parse_args()

    filtros = filtros_soltos(args.filtros)
    dias = args.dias or filtros.get("dias") or 30
    desde = datetime.now(timezone.utc) - timedelta(days=dias)

    ids = {i.strip() for i in args.execucoes.split(",") if i.strip()}
    if ids:
        filtros = {"execucoes": sorted(ids)}
        execucoes = [e for e in com_janelas(execucoes_registradas()) if e["execucao"] in ids]
    else:
        execucoes = [
            e for e in com_janelas(execucoes_registradas())
            if e["inicio"] >= desde
            and (not filtros.get("comando") or e.get("comando") == filtros["comando"])
            and (not filtros.get("item") or (e.get("item") or "").upper() == filtros["item"])
        ][-args.limite:]

    resultado = [medir(e, args.lenta_ms) for e in execucoes]
    filtros_aplicados = filtros if ids else {"dias": dias, **{k: v for k, v in filtros.items() if k != "dias"}}

    if args.json:
        json.dump({"filtros": filtros_aplicados, "execucoes": resultado}, sys.stdout, ensure_ascii=False, separators=(",", ":"))
        print()
    elif resultado:
        print(f"Execuções locais ({len(resultado)}), filtros {filtros_aplicados}:\n")
        print(tabela(resultado))
    else:
        print(f"Nenhuma execução local com os filtros {filtros_aplicados}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
