#!/usr/bin/env python3
"""
Verificação estrutural do plugin `vo` (roda na CI e antes de cada PR).

    python3 scripts/verificar.py [--base origin/main]

Confere:
  - marketplace.json e plugin.json válidos, com o mesmo nome e versão semver;
  - cada skill em plugins/vo/skills/<nome>/SKILL.md com frontmatter: `name`
    igual à pasta (kebab-case), `description` de até 1024 caracteres;
  - cada agente em plugins/vo/agents/<nome>.md com `name` igual ao arquivo e
    `description`;
  - arquivos `shared/*.md` e `scripts/*` citados pelas skills e agentes existem;
  - o README do plugin cita todos os comandos, skills de apoio e agentes;
  - o CHANGELOG tem uma seção da versão atual;
  - o header X-VO-Cliente do .mcp.json leva essa versão;
  - com --base, a versão subiu se algo em plugins/ mudou.

Só usa a biblioteca padrão do Python.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PLUGIN = RAIZ / "plugins" / "vo"
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

erros: list[str] = []


def erro(msg: str) -> None:
    erros.append(msg)


def frontmatter(caminho: Path) -> dict:
    """Lê o bloco `---` do início de um Markdown: chaves simples e listas `- x`."""
    texto = caminho.read_text(encoding="utf-8")
    if not texto.startswith("---\n"):
        erro(f"{caminho.relative_to(RAIZ)}: sem frontmatter")
        return {}

    fim = texto.find("\n---", 4)
    if fim == -1:
        erro(f"{caminho.relative_to(RAIZ)}: frontmatter sem fechamento")
        return {}

    dados: dict = {}
    chave = None
    for linha in texto[4:fim].splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        if linha.startswith("  - ") or linha.startswith("- "):
            if chave:
                dados.setdefault(chave, [])
                if isinstance(dados[chave], list):
                    dados[chave].append(linha.split("- ", 1)[1].strip())
            continue
        if linha.startswith(" "):
            continue
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            chave = chave.strip()
            valor = valor.strip().strip('"').strip("'")
            dados[chave] = valor if valor else []
    return dados


def corpo(caminho: Path) -> str:
    texto = caminho.read_text(encoding="utf-8")
    fim = texto.find("\n---", 4)
    return texto[fim + 4 :] if texto.startswith("---\n") and fim != -1 else texto


def manifestos() -> tuple[str, str]:
    marketplace = json.loads((RAIZ / ".claude-plugin" / "marketplace.json").read_text())
    plugin = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())

    nomes = [p.get("name") for p in marketplace.get("plugins", [])]
    if plugin.get("name") not in nomes:
        erro(f"marketplace.json não lista o plugin `{plugin.get('name')}`")

    versao = plugin.get("version", "")
    if not SEMVER.match(versao):
        erro(f"plugin.json: versão `{versao}` não é semver (X.Y.Z)")

    return plugin.get("name", ""), versao


def cliente(versao: str) -> None:
    """O header X-VO-Cliente do .mcp.json leva a versão do plugin (métricas do VO)."""
    mcp = json.loads((PLUGIN / ".mcp.json").read_text())
    header = mcp.get("mcpServers", {}).get("vo", {}).get("headers", {}).get("X-VO-Cliente")
    if header != f"vo-plugin/{versao}":
        erro(f".mcp.json: X-VO-Cliente é `{header}`, esperado `vo-plugin/{versao}`")


def skills() -> list[tuple[str, dict]]:
    encontradas = []
    raiz = PLUGIN / "skills"
    for pasta in sorted(raiz.iterdir() if raiz.exists() else []):
        if not pasta.is_dir():
            continue
        arquivo = pasta / "SKILL.md"
        if not arquivo.exists():
            erro(f"skills/{pasta.name}: sem SKILL.md")
            continue

        meta = frontmatter(arquivo)
        if meta.get("name") != pasta.name:
            erro(f"skills/{pasta.name}: `name` ({meta.get('name')}) diferente da pasta")
        if not KEBAB.match(pasta.name):
            erro(f"skills/{pasta.name}: nome fora de kebab-case")
        descricao = meta.get("description", "")
        if not descricao:
            erro(f"skills/{pasta.name}: sem `description`")
        elif len(descricao) > 1024:
            erro(f"skills/{pasta.name}: `description` com mais de 1024 caracteres")
        if len(corpo(arquivo).splitlines()) > 500:
            erro(f"skills/{pasta.name}: mais de 500 linhas; mova detalhes para shared/")

        encontradas.append((pasta.name, meta))
    return encontradas


def agentes() -> list[str]:
    nomes = []
    for arquivo in sorted((PLUGIN / "agents").glob("*.md")):
        meta = frontmatter(arquivo)
        if meta.get("name") != arquivo.stem:
            erro(f"agents/{arquivo.name}: `name` ({meta.get('name')}) diferente do arquivo")
        if not meta.get("description"):
            erro(f"agents/{arquivo.name}: sem `description`")
        nomes.append(arquivo.stem)
    return nomes


def referencias() -> None:
    """`shared/x.md` e `scripts/x` citados precisam existir."""
    arquivos = [p for pasta in ("skills", "agents", "shared") for p in (PLUGIN / pasta).rglob("*.md")]
    for arquivo in arquivos:
        texto = arquivo.read_text(encoding="utf-8")
        for ref in set(re.findall(r"(?:shared|scripts)/[\w.-]+\.(?:md|sh|py|mjs)", texto)):
            if not (PLUGIN / ref).exists():
                erro(f"{arquivo.relative_to(RAIZ)}: cita `{ref}`, que não existe")


def regras_pedidas() -> None:
    """Os nomes passados a `regras.sh` precisam existir em shared/."""
    for arquivo in (PLUGIN / "skills").rglob("SKILL.md") if (PLUGIN / "skills").exists() else []:
        for linha in re.findall(r"scripts/regras\.sh\"?\s+([^`]+)`", arquivo.read_text(encoding="utf-8")):
            for nome in linha.split():
                if not (PLUGIN / "shared" / f"{nome}.md").exists():
                    erro(f"{arquivo.relative_to(RAIZ)}: pede a regra `{nome}`, que não existe em shared/")


def scripts_liberados(skills_: list[tuple[str, dict]]) -> None:
    """
    Todo script chamado com `!` numa skill precisa estar no `allowed-tools`
    dela: sem isso o Claude Code bloqueia o pré-processamento.
    """
    for nome, meta in skills_:
        texto = (PLUGIN / "skills" / nome / "SKILL.md").read_text(encoding="utf-8")
        permitidos = meta.get("allowed-tools", "")
        permitidos = " ".join(permitidos) if isinstance(permitidos, list) else permitidos
        for script in set(re.findall(r"!`sh [^`]*scripts/([\w.-]+\.sh)", texto)):
            if f"scripts/{script}" not in permitidos:
                erro(f"skills/{nome}: chama scripts/{script} com `!`, mas não o libera em `allowed-tools`")


def readme(skills_: list[tuple[str, dict]], agentes_: list[str]) -> None:
    texto = (PLUGIN / "README.md").read_text(encoding="utf-8")
    for nome, meta in skills_:
        comando = meta.get("user-invocable", "true") != "false"
        alvo = f"/vo:{nome}" if comando else f"`{nome}`"
        if alvo not in texto:
            erro(f"README do plugin não cita {alvo}")
    for nome in agentes_:
        if f"`{nome}`" not in texto:
            erro(f"README do plugin não cita o agente `{nome}`")


def changelog(versao: str) -> None:
    texto = (PLUGIN / "CHANGELOG.md").read_text(encoding="utf-8")
    if not re.search(rf"^## {re.escape(versao)}\b", texto, re.M):
        erro(f"CHANGELOG.md sem a seção `## {versao}`")


def versao_subiu(base: str, versao: str) -> None:
    mudou = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD", "--", "plugins/"],
        cwd=RAIZ, capture_output=True, text=True, check=True,
    ).stdout.strip()
    if not mudou:
        return

    anterior = subprocess.run(
        ["git", "show", f"{base}:plugins/vo/.claude-plugin/plugin.json"],
        cwd=RAIZ, capture_output=True, text=True,
    )
    if anterior.returncode != 0:
        return  # o plugin ainda não existia na base

    if json.loads(anterior.stdout).get("version") == versao:
        erro(f"plugins/ mudou desde {base}, mas a versão continua {versao}; suba a versão e o CHANGELOG")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", help="ref para conferir se a versão subiu (ex.: origin/main)")
    args = parser.parse_args()

    _nome, versao = manifestos()
    cliente(versao)
    skills_ = skills()
    agentes_ = agentes()
    referencias()
    regras_pedidas()
    scripts_liberados(skills_)
    readme(skills_, agentes_)
    changelog(versao)
    if args.base:
        versao_subiu(args.base, versao)

    if erros:
        print("verificar.py encontrou problemas:")
        for msg in erros:
            print(f"  - {msg}")
        return 1

    print(f"ok: plugin vo {versao}, {len(skills_)} skills, {len(agentes_)} agentes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
