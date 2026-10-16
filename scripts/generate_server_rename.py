#!/usr/bin/env python3
"""
Gera output/server_rename.sh — script autossuficiente para o servidor.

Lê localmente:
  - output/import_users.txt        → usernames válidos (ordem BOCA)
  - animeitor_photos_converted/    → quais usernames têm foto (.webp)
  - animeitor_sounds_converted/    → quais usernames têm som (.mp3)

Gera um shell script com a lista de nomes corretos embutida. No servidor,
o script ordena os arquivos numericamente, mapeia posição-a-posição com a
lista correta e executa mv/rm conforme necessário — sem precisar de nenhum
arquivo de dados extra no servidor.

Uso:
    python3 scripts/generate_server_rename.py \\
        --photos-dir /caminho/no/servidor/photos \\
        --sounds-dir /caminho/no/servidor/sounds \\
        [--host nome-da-vm]                         # gera output/server_rename.sh
"""
import argparse
import re
from pathlib import Path

BASE          = Path(__file__).resolve().parent.parent
IMPORT_USERS  = BASE / "output" / "import_users.txt"
PHOTOS_SRC    = BASE / "animeitor_photos_converted"
SOUNDS_SRC    = BASE / "animeitor_sounds_converted"
OUT_SCRIPT    = BASE / "output" / "server_rename.sh"


def parse_usernames(path: Path) -> list[str]:
    users = []
    with open(path) as f:
        for line in f:
            m = re.match(r"username=(team\w+)", line.strip())
            if m:
                users.append(m.group(1))
    return users


def local_file_map(directory: Path) -> dict[str, str]:
    """username → extensão (ex: '.webp')"""
    return {f.stem: f.suffix for f in directory.iterdir() if f.is_file()}


def sort_key(name: str) -> tuple:
    # Prefixo da competição (ex: teamxa) + número de 3 dígitos
    m = re.match(r"(team\w*?)(\d{3})(\.\w+)?$", name)
    if m:
        return (m.group(1), int(m.group(2)))
    return ("~", 0)


def make_block(label: str, remote_dir: str, correct_names: list[str]) -> str:
    """Gera o bloco bash para um diretório com a lista de nomes corretos embutida."""
    names_str = " ".join(f'"{n}"' for n in correct_names)
    return f"""
echo ""
echo "=== {label}: {remote_dir} ==="
cd "{remote_dir}"

CORRECT=({names_str})

# Ordenar arquivos team* por prefixo da competição e número
mapfile -t FILES < <(ls | grep -E '^team' | python3 -c "
import sys, re
names = sys.stdin.read().split()
def key(n):
    m = re.match(r'(team\\w*?)(\\d{{3}})(\\.\\w+)?$', n)
    return (m.group(1), int(m.group(2))) if m else ('~', 0)
print('\\n'.join(sorted(names, key=key)))
")

N_CORRECT=${{#CORRECT[@]}}
N_FILES=${{#FILES[@]}}
RENAMED=0; KEPT=0; REMOVED=0; SKIPPED=0

IDX=0
for f in "${{FILES[@]}}"; do
    if [ $IDX -lt $N_CORRECT ]; then
        expected="${{CORRECT[$IDX]}}"
        if [ "$f" = "$expected" ]; then
            echo "  OK     $f"
            ((KEPT++)) || true
        elif [ -e "$expected" ]; then
            echo "  SKIP   $f (destino $expected já existe — removendo duplicata antiga)"
            rm "$f"
            ((SKIPPED++)) || true
            IDX=$((IDX - 1))  # não avança: o expected já está no lugar certo
        else
            mv "$f" "$expected"
            echo "  MV     $f → $expected"
            ((RENAMED++)) || true
        fi
        ((IDX++)) || true
    else
        rm "$f"
        echo "  RM     $f (fora do conjunto esperado)"
        ((REMOVED++)) || true
    fi
done

echo "  → MV=$RENAMED  OK=$KEPT  SKIP/RM_dup=$SKIPPED  RM_extra=$REMOVED  (esperados=$N_CORRECT encontrados=$N_FILES)"
"""


def parse_args():
    parser = argparse.ArgumentParser(description="Gera o script de renomeação de mídias do animeitor no servidor.")
    parser.add_argument("--photos-dir", required=True, help="Pasta das fotos no servidor")
    parser.add_argument("--sounds-dir", required=True, help="Pasta dos sons no servidor")
    parser.add_argument("--host", default="<host>", help="Nome da VM, usado só nas instruções impressas")
    return parser.parse_args()


def main():
    args = parse_args()
    usernames = parse_usernames(IMPORT_USERS)
    photos_map = local_file_map(PHOTOS_SRC)
    sounds_map = local_file_map(SOUNDS_SRC)
    valid = set(usernames)

    # Lista ordenada de nomes de arquivo corretos para cada diretório
    correct_photos = sorted(
        [u + ext for u, ext in photos_map.items() if u in valid],
        key=sort_key
    )
    correct_sounds = sorted(
        [u + ext for u, ext in sounds_map.items() if u in valid],
        key=sort_key
    )

    print(f"Usernames em import_users.txt : {len(usernames)}")
    print(f"Fotos esperadas no servidor   : {len(correct_photos)}")
    print(f"Sons esperados no servidor    : {len(correct_sounds)}")

    header = """\
#!/usr/bin/env bash
# Gerado por scripts/generate_server_rename.py
# Script autossuficiente: lista de nomes corretos embutida.
# Uso: bash server_rename.sh
set -euo pipefail
"""

    body  = make_block("photos", args.photos_dir, correct_photos)
    body += make_block("sounds", args.sounds_dir, correct_sounds)
    body += '\necho ""\necho "Concluído."\n'

    OUT_SCRIPT.write_text(header + body)
    OUT_SCRIPT.chmod(0o755)
    print(f"\nScript gerado: {OUT_SCRIPT}")
    print("Para usar:")
    print(f"  gcloud compute scp {OUT_SCRIPT.relative_to(BASE)} {args.host}:~/")
    print(f"  gcloud compute ssh {args.host} -- bash {OUT_SCRIPT.name}")


if __name__ == "__main__":
    main()
