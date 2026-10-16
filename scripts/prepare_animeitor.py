#!/usr/bin/env python3
"""
Gera os arquivos do animeitor a partir dos times inscritos e dos usuários do BOCA.

Usa a mesma .env do main.py para saber:
  - input_files / competition_codes  → planilha de times de cada competição
  - competition_code                 → output/users_{competition_code}{código}.xlsx
  - column_sheet_*                   → nomes das colunas de time, instituição e username

Gera:
  - output/animeitor/{código}/basic.toml        → [titulo] + [[sedes]] no formato do animeitor
  - output/animeitor/{código}/basic_secret.toml → salt + [[secrets]] (um secret por nome de sede)
  - output/animeitor_midia.xlsx    → (opcional) links de foto/música de cada username
                                     e o nome de arquivo esperado pelo animeitor

Em cada basic.toml:
  - [titulo] e a primeira sede, ambos com o nome da competição (--name) e o prefixo do username
  - Uma sede para cada valor distinto de cada coluna passada em --group-by

Os secrets seguem o padrão nome da sede sem acentos/símbolos + sufixo (ex: "Sede Norte" → "sedenorte2k26").

Exemplo (na raiz do projeto, depois de rodar main.py), com competition_codes=["a", "b"] na .env:
    python scripts/prepare_animeitor.py \\
        --name "a=Competição A" --name "b=Competição B" \\
        --medals a=3,6,9 --medals b=1,2,3 \\
        --group-by "QTD pessoas" --label "QTD pessoas={} pessoas" \\
        --group-by "Nome da Instituição de Ensino" \\
        --group-medals "Nome da Instituição de Ensino=1,0,0" \\
        --photo-column "Link da foto" \\
        --music-column "Link da música"
"""
import argparse
import datetime
import json
import os
import re
import unicodedata
from pathlib import Path

import dotenv
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
NO_MEDALS = (0, 0, 0)


def parse_medals(text):
    medals = tuple(int(v) for v in text.split(","))
    if len(medals) != 3:
        raise argparse.ArgumentTypeError(f"medalhas devem ser ouro,prata,bronze: '{text}'")
    return medals


def parse_mapping(items, value_parser=str):
    """Converte ['chave=valor', ...] em dicionário."""
    mapping = {}
    for item in items or []:
        key, sep, value = item.partition("=")
        if not sep:
            raise SystemExit(f"Parâmetro inválido (esperado CHAVE=VALOR): '{item}'")
        mapping[key] = value_parser(value)
    return mapping


def parse_args():
    parser = argparse.ArgumentParser(description="Gera a configuração de sedes do animeitor.")
    parser.add_argument("--group-by", action="append", default=[], metavar="COLUNA",
                        help="Coluna da planilha de times usada para dividir em sedes (repetível)")
    parser.add_argument("--label", action="append", metavar="COLUNA=MODELO",
                        help="Modelo do nome da sede para a coluna, com {} no lugar do valor (padrão: {})")
    parser.add_argument("--group-medals", action="append", metavar="COLUNA=O,P,B",
                        help="Medalhas das sedes da coluna (padrão: 0,0,0)")
    parser.add_argument("--name", action="append", metavar="CÓDIGO=NOME",
                        help="Nome da competição, usado no [titulo] e na primeira sede (padrão: código em maiúsculas)")
    parser.add_argument("--medals", action="append", metavar="CÓDIGO=O,P,B",
                        help="Medalhas da sede geral da competição (padrão: 0,0,0)")
    parser.add_argument("--photo-column", help="Coluna com o link da foto do time")
    parser.add_argument("--music-column", help="Coluna com o link da música do time")
    parser.add_argument("--salt", default="salt", help="Valor de salt do basic_secret.toml (padrão: salt)")
    parser.add_argument("--secret-suffix", default=f"2k{datetime.date.today().year % 100:02d}",
                        help="Sufixo dos secrets (padrão: 2k + ano atual, ex: 2k26)")
    parser.add_argument("--output-dir", default="output/animeitor/{}",
                        help="Pasta dos arquivos TOML, com {} no lugar do código da competição")
    parser.add_argument("--output-media", default="output/animeitor_midia.xlsx")
    return parser.parse_args()


def clean(series):
    """Remove espaços nas pontas e repetidos, como em file_management.py."""
    return series.astype(str).str.split().str.join(" ")


def format_value(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def load_competition(code, times_file, users_file, extra_columns, env):
    team_column = env["column_sheet_team_name"]
    institution_column = env["column_sheet_institution"]
    full_name_column = env["column_sheet_team_name_full"]
    username_column = env["column_sheet_username"]

    times = pd.read_excel(times_file)
    users = pd.read_excel(users_file)

    missing_columns = [c for c in extra_columns if c not in times.columns]
    if missing_columns:
        raise SystemExit(f"[{code}] Colunas não encontradas em {times_file.name}: {missing_columns}")

    # Mesma chave usada pelo file_management.py para o nome completo do time
    times["_full_name"] = "[" + clean(times[institution_column]) + "] " + clean(times[team_column])
    duplicated = times["_full_name"][times["_full_name"].duplicated()]
    if not duplicated.empty:
        raise SystemExit(f"[{code}] Times duplicados, impossível cruzar com os usuários: {duplicated.tolist()}")

    # Colunas que também existem na planilha de usuários vêm de lá
    extra_columns = [c for c in dict.fromkeys(extra_columns) if c not in users.columns]
    merged = users.merge(
        times[["_full_name"] + extra_columns],
        left_on=full_name_column, right_on="_full_name", how="left", validate="one_to_one",
    )
    missing = merged[merged["_full_name"].isna()]
    if not missing.empty:
        raise SystemExit(f"[{code}] Usuários sem time correspondente: {missing[full_name_column].tolist()}")

    return merged.rename(columns={username_column: "username"}).sort_values("username").reset_index(drop=True)


def username_prefix(usernames):
    """Prefixo comum dos usernames da competição (ex: teamxa001 → teamxa)."""
    return os.path.commonprefix([u[:-3] for u in usernames])


def toml_string(value):
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def toml_block(header, name, codes, medals):
    ouro, prata, bronze = medals
    return "\n".join([
        header,
        f"name = {toml_string(name)}",
        f"codes = [{', '.join(toml_string(c) for c in codes)}]",
        f"ouro = {ouro}",
        f"prata = {prata}",
        f"bronze = {bronze}",
        "",
    ])


def build_sedes(code, df, args, names, medals, labels, group_medals):
    """Lista de (nome, codes, medalhas); a primeira é o [titulo]."""
    name = names.get(code, code.upper())
    prefix = username_prefix(df["username"])
    competition_medals = medals.get(code, NO_MEDALS)
    sedes = [
        (name, [prefix], competition_medals),
        (name, [prefix], competition_medals),
    ]

    for column in args.group_by:
        label = labels.get(column, "{}")
        for value, group in df.dropna(subset=[column]).groupby(column):
            sedes.append((label.format(format_value(value)), group["username"].tolist(), group_medals.get(column, NO_MEDALS)))

    names_seen = [sede[0] for sede in sedes[1:]]
    duplicated = {n for n in names_seen if names_seen.count(n) > 1}
    if duplicated:
        raise SystemExit(f"[{code}] Sedes com nomes repetidos (use --label para diferenciar): {sorted(duplicated)}")
    return sedes


def build_basic(sedes, comment):
    blocks = [f"# {comment}\n"]
    for i, (name, codes, medals) in enumerate(sedes):
        blocks.append(toml_block("[titulo]" if i == 0 else "[[sedes]]", name, codes, medals))
    return "\n".join(blocks)


def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", text.lower())


def build_secret(sedes, args):
    blocks = [f"salt = {toml_string(args.salt)}\n"]
    used = set()
    # [titulo] e a primeira sede têm o mesmo nome: um secret por nome
    for name in dict.fromkeys(sede[0] for sede in sedes):
        base = slug(name)
        secret, counter = base + args.secret_suffix, 2
        while secret in used:
            secret, counter = f"{base}{counter}{args.secret_suffix}", counter + 1
        used.add(secret)
        blocks.append("\n".join(["[[secrets]]", f"name = {toml_string(name)}", f"secret = {toml_string(secret)}", ""]))
    return "\n".join(blocks)


def build_media(competitions, args, full_name_column):
    rows = []
    for code, df in competitions.items():
        for _, row in df.iterrows():
            media = {"Competição": code, "username": row["username"], "Time": row[full_name_column]}
            for column, folder, ext, label in [(args.photo_column, "photos", "webp", "foto"),
                                               (args.music_column, "sounds", "mp3", "música")]:
                if column:
                    media[f"Link {label}"] = row[column]
                    media[f"Arquivo {label}"] = f"{folder}/{row['username']}.{ext}" if pd.notna(row[column]) else None
            rows.append(media)
    return pd.DataFrame(rows)


def main():
    args = parse_args()
    dotenv.load_dotenv(BASE / ".env")
    env = os.environ

    names = parse_mapping(args.name)
    medals = parse_mapping(args.medals, parse_medals)
    labels = parse_mapping(args.label)
    group_medals = parse_mapping(args.group_medals, parse_medals)
    for column in list(labels) + list(group_medals):
        if column not in args.group_by:
            raise SystemExit(f"Coluna '{column}' usada em --label/--group-medals mas não informada em --group-by")

    input_path = BASE / env["input_path"]
    output_path = BASE / env["output_path"]
    input_files = json.loads(env["input_files"])
    codes = json.loads(env["competition_codes"])
    if len(input_files) != len(codes):
        raise SystemExit("input_files e competition_codes da .env devem ter o mesmo tamanho")

    extra_columns = args.group_by + [c for c in (args.photo_column, args.music_column) if c]
    competitions = {
        code: load_competition(
            code,
            input_path / input_file,
            output_path / f"users_{env['competition_code']}{code}.xlsx",
            extra_columns,
            env,
        )
        for input_file, code in zip(input_files, codes)
    }

    for code, df in competitions.items():
        sedes = build_sedes(code, df, args, names, medals, labels, group_medals)
        output_dir = BASE / args.output_dir.format(code)
        output_dir.mkdir(parents=True, exist_ok=True)
        comment = f"{names.get(code, code.upper())} ({code}) — {len(df)} times"
        (output_dir / "basic.toml").write_text(build_basic(sedes, comment), encoding="utf-8")
        (output_dir / "basic_secret.toml").write_text(build_secret(sedes, args), encoding="utf-8")
        print(f"Arquivos criados: {args.output_dir.format(code)}/basic.toml, basic_secret.toml")

    if args.photo_column or args.music_column:
        media_file = BASE / args.output_media
        build_media(competitions, args, env["column_sheet_team_name_full"]).to_excel(media_file, index=False)
        print(f"Arquivo criado: {args.output_media}")

    for code, df in competitions.items():
        print(f"\n[{code}] {len(df)} times — prefixo {username_prefix(df['username'])}")
        for column in args.group_by:
            print(f"  {column}: {df[column].value_counts(dropna=False).sort_index().to_dict()}")
            without_value = df[df[column].isna()]["username"].tolist()
            if without_value:
                print(f"    Sem valor (fora das sedes): {without_value}")
        for column, label in [(args.photo_column, "foto"), (args.music_column, "música")]:
            if column:
                without_media = df[df[column].isna()]["username"].tolist()
                if without_media:
                    print(f"  Sem {label}: {without_media}")


if __name__ == "__main__":
    main()
