#!/bin/sh
# Pré-condições dos comandos do plugin vo. Imprime linhas chave=valor; a
# última é `situacao=ok` ou `situacao=bloqueado`.
#
#   sh pre-condicoes.sh <pasta do projeto> [--sem-config] [--git] [--gh]
#
#   --sem-config  não exige .claude/vo.json (usado por /vo:configurar)
#   --git         exige um repositório git
#   --gh          exige o GitHub CLI autenticado
set -u

projeto="${1:-.}"
shift 2>/dev/null || true
exige_config=1
exige_git=0
exige_gh=0
for opcao in "$@"; do
  case "$opcao" in
    --sem-config) exige_config=0 ;;
    --git) exige_git=1 ;;
    --gh) exige_gh=1 ;;
  esac
done

bloqueado=0
raiz="$projeto"

if command -v git >/dev/null 2>&1; then
  if top="$(git -C "$projeto" rev-parse --show-toplevel 2>/dev/null)"; then
    raiz="$top"
    echo "git=ok"
    echo "repositorio=$top"
    echo "branch=$(git -C "$top" branch --show-current 2>/dev/null)"
  else
    echo "git=fora-de-repositorio"
    [ "$exige_git" = 1 ] && bloqueado=1
  fi
else
  echo "git=ausente"
  [ "$exige_git" = 1 ] && bloqueado=1
fi

config="$raiz/.claude/vo.json"
if [ -f "$config" ]; then
  echo "config=ok"
  echo "config_arquivo=$config"
  # Sem depender de jq: os campos são simples.
  for campo in projeto_id projeto quadro; do
    valor="$(sed -n "s/.*\"$campo\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" "$config" | head -n 1)"
    [ -n "$valor" ] && echo "$campo=$valor"
  done
else
  echo "config=ausente"
  [ "$exige_config" = 1 ] && bloqueado=1
fi

if [ "$exige_gh" = 1 ]; then
  if ! command -v gh >/dev/null 2>&1; then
    echo "gh=ausente"
    bloqueado=1
  elif gh auth status >/dev/null 2>&1; then
    echo "gh=ok"
  else
    echo "gh=deslogado"
    bloqueado=1
  fi
fi

if [ "$bloqueado" = 1 ]; then
  echo "situacao=bloqueado"
else
  echo "situacao=ok"
fi
