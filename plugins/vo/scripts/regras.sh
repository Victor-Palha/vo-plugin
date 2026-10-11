#!/bin/sh
# Imprime as regras comuns pedidas (shared/<nome>.md), para os comandos as
# incluírem com `!` sem depender de permissão de leitura fora do repositório.
#
#   sh regras.sh transparencia skills-do-projeto
dir="$(cd "$(dirname "$0")/../shared" && pwd)"
for nome in "$@"; do
  if [ -f "$dir/$nome.md" ]; then
    cat "$dir/$nome.md"
    echo
  else
    echo "(regra \`$nome\` não encontrada no plugin)"
  fi
done
