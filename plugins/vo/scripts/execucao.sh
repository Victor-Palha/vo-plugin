#!/bin/sh
# Marca o início de uma execução de um comando do plugin (VO-114).
#
#   sh execucao.sh <comando> <session_id> [argumentos do comando...]
#
# Grava {comando, execucao, item} num arquivo da sessão, fora do repositório.
# O hook PreToolUse (injetar_execucao.py) lê esse arquivo e anexa o argumento
# reservado `_vo` a cada chamada ao MCP do VO, para as métricas saberem de
# qual comando e execução ela veio. O VO remove `_vo` antes da ferramenta.
set -eu

comando="${1:-}"
sessao="${2:-}"
shift 2 2>/dev/null || true

if [ -z "$comando" ] || [ -z "$sessao" ]; then
  echo "execucao=sem-sessao"
  exit 0
fi

dir="${XDG_CACHE_HOME:-$HOME/.cache}/vo-plugin/execucoes"
mkdir -p "$dir"

execucao="$(date -u +%Y%m%dT%H%M%SZ)-$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"
# A primeira chave de item nos argumentos (ex.: VO-12), se houver.
item="$(printf '%s ' "$@" | grep -oE '[A-Za-z][A-Za-z0-9]*-[0-9]+' | head -n 1 | tr '[:lower:]' '[:upper:]' || true)"

printf '{"comando":"%s","execucao":"%s","item":"%s"}\n' "$comando" "$execucao" "$item" > "$dir/$sessao.json"

# Arquivos de sessões com mais de 2 dias não servem mais.
find "$dir" -name '*.json' -mtime +2 -delete 2>/dev/null || true

echo "execucao=$execucao"
