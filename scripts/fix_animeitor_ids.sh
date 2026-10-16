#!/usr/bin/env bash
# Remove arquivos de mídia do animeitor que ficaram com a numeração deslocada.
#
# Caso de uso: alguns times não enviaram mídia e os arquivos seguintes foram
# numerados com um deslocamento em relação ao username real no BOCA. Depois que
# os arquivos corretos já estão na pasta, este script remove as cópias antigas
# ({prefixo}{N}) quando o arquivo correto ({prefixo}{N + deslocamento}) existe.
#
# Uso:
#   bash fix_animeitor_ids.sh [--dry-run] <pasta> <prefixo> <de> <até> <deslocamento>
#
# Exemplo (remove teamxa009–teamxa057 se teamxa011–teamxa059 existirem):
#   bash fix_animeitor_ids.sh --dry-run /caminho/no/servidor/photos teamxa 9 57 2

set -euo pipefail

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    shift
fi

if [[ $# -ne 5 ]]; then
    echo "Uso: bash $0 [--dry-run] <pasta> <prefixo> <de> <até> <deslocamento>"
    exit 1
fi

DIR="$1"
PREFIX="$2"
FROM="$3"     # número inicial (inclusivo)
TO="$4"       # número final (inclusivo)
OFFSET="$5"   # quanto somar ao número antigo para chegar ao correto

if [[ ! -d "$DIR" ]]; then
    echo "ERRO: diretório não encontrado: $DIR"
    exit 1
fi

$DRY_RUN && echo "MODO DRY-RUN — nenhum arquivo será alterado"
echo ""
echo "=== $DIR: removendo ${PREFIX}$(printf "%03d" "$FROM")–${PREFIX}$(printf "%03d" "$TO") ==="

count=0
for num in $(seq "$FROM" "$TO"); do
    old_num=$(printf "%03d" "$num")
    correct_num=$(printf "%03d" "$((num + OFFSET))")

    for f in "$DIR/${PREFIX}${old_num}".*; do
        [[ -e "$f" ]] || continue
        ext="${f##*.}"
        correct="$DIR/${PREFIX}${correct_num}.${ext}"

        if [[ ! -e "$correct" ]]; then
            echo "  AVISO: arquivo correto $correct não existe — pulando deleção de $f"
            continue
        fi

        if $DRY_RUN; then
            echo "  DRY  rm ${PREFIX}${old_num}.${ext}  (correto: ${PREFIX}${correct_num}.${ext} ✓)"
        else
            rm "$f"
            echo "  DEL  ${PREFIX}${old_num}.${ext}  (correto: ${PREFIX}${correct_num}.${ext} ✓)"
        fi
        ((count++)) || true
    done
done

echo "  Total: $count arquivo(s) removido(s)"
if $DRY_RUN; then
    echo ""
    echo "Dry-run concluído. Para aplicar, rode sem --dry-run."
fi
