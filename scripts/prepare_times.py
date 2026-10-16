#!/usr/bin/env python3
"""
Prepara as planilhas de times de cada competição a partir da planilha de inscrições.

- Remove colunas sem cabeçalho (ex: resumos ao lado das respostas)
- Renomeia colunas para os nomes usados na .env (column_sheet_*)
- Remove espaços extras e normaliza o nome das instituições (INSTITUTION_MAP)
- Separa os times por competição, a partir de uma coluna de categoria (--category-column)
  ou gera uma única competição (--code)

Saída: input/[CÓDIGO] Times.xlsx (configurável em --output)

Exemplos (na raiz do projeto):
    # Uma aba com uma coluna de categoria → uma planilha por categoria
    python scripts/prepare_times.py --source "input/inscricoes.xlsx" \\
        --category-column "Qual categoria seu time gostaria de participar?" \\
        --category "Maratona=M3" --category "Meia Maratona=M4"

    # Uma aba por competição, renomeando colunas e definindo o local de prova
    python scripts/prepare_times.py --source "input/inscricoes.xlsx" --sheet "CCL" --code CCL \\
        --rename "Nome Time=Nome Completo" --rename "Instituicao=Nome da Instituição de Ensino" \\
        --location "CCL"
"""
import argparse
import os
from pathlib import Path

import dotenv
import pandas as pd

BASE = Path(__file__).resolve().parent.parent

INSTITUTION_MAP = {
    "CEFET-Timóteo": "CEFETMG-TIM",
    "CEFET/BH": "CEFETMG-BH",
    "CEFET/Divinópolis": "CEFETMG-DIV",
    "CEFET/Leopoldina": "CEFETMG-LEO",
    "IFMG/Formiga": "IFMG-FOR",
    "IFMG/Ouro Branco": "IFMG-OURO",
    "IFSULDEMINAS/Muzambinho": "IFSULDEMINAS-MUZ",
    "IFSULDEMINAS - Campus Muzambinho": "IFSULDEMINAS-MUZ",
    "IFSULDEMINAS/Poços de Caldas": "IFSULDEMINAS-POCOS",
    "IFTM/Patrocínio": "IFTM-PAT",
    "IFTM/Uberaba": "IFTM-UPT",
    "IFTM- Campina Verde -MG": "IFTM-CV",
    "INATEL/Santa Rita do Sapucaí": "INATEL",
    "Inatel": "INATEL",
    "PUC/BH": "PUC-BH",
    "PUC Minas - BH": "PUC-BH",
    "UFJF/Juiz de Fora": "UFJF",
    "UFMG/BH": "UFMG",
    "UFMG - BH": "UFMG",
    "UFG - Universidade Federal de Goiás": "UFG",
    "UFSJ/CAP": "UFSJ-CAP",
    "UFSJ/São João del Rei": "UFSJ",
    "UFU/Monte Carmelo": "UFU-MC",
    "UFU/Uberlândia": "UFU-UDI",
    "UFV/Florestal": "UFV-FLO",
    "UFV/Viçosa": "UFV",
    "UFV-Viçosa": "UFV",
    "Universidade Federal de Viçosa": "UFV",
    "UFVJM": "UFVJM",
    "UNIFAGOC/Ubá": "UNIFAGOC",
    "UNIFEI/Itabira": "UNIFEI-ITABIRA",
    "UNIFEI/Itajubá": "UNIFEI",
    "UNIFEI-Itajubá": "UNIFEI",
    "Não se Aplica": "GERAL",
    "CEFET-MG - Belo Horizonte": "CEFETMG-BH",
    "CEFET-MG - Divinópolis": "CEFETMG-DIV",
    "CEFET-MG - Leopoldina": "CEFETMG-LEO",
    "IFMG - Campus Formiga": "IFMG-FOR",
    "IFMG - Ouro Branco": "IFMG-OURO",
    "IFTM - Campina Verde": "IFTM-CV",
    "IFTM - Campus Campina Verde": "IFTM-CV",
    "IFTM - Patrocinio": "IFTM-PAT",
    "IFTM - Uberaba Parque Tecnológico": "IFTM-UPT",
    "PUC Minas - Belo Horizonte": "PUC-BH",
    "UFJF - Juiz de Fora": "UFJF",
    "UFMG - Belo Horizonte": "UFMG",
    "UFSJ - Ouro Branco": "UFSJ-CAP",
    "UFSJ - São João del-Rei": "UFSJ",
    "UFU - Uberlândia": "UFU-UDI",
    "UFV - Florestal": "UFV-FLO",
    "UFV - Viçosa": "UFV",
    "UNIFEI - Itabira": "UNIFEI-ITABIRA",
    "UNIFEI - Itajubá": "UNIFEI",
}


def normalize_institutions(df, col, label):
    substitutions = []
    def replace(val):
        normalized = INSTITUTION_MAP.get(val)
        if normalized and normalized != val:
            substitutions.append((val, normalized))
            return normalized
        if normalized is None and pd.notna(val):
            substitutions.append((val, f"[SEM MAPEAMENTO - mantido: {val}]"))
        return val
    df[col] = df[col].apply(replace)
    print(f"\n=== Substituições em {label} ===")
    seen = set()
    for orig, norm in substitutions:
        key = (orig, norm)
        if key not in seen:
            print(f"  {orig!r:50s} → {norm!r}")
            seen.add(key)
    return df


def parse_mapping(items):
    """Converte ['chave=valor', ...] em dicionário."""
    mapping = {}
    for item in items or []:
        key, sep, value = item.partition("=")
        if not sep:
            raise SystemExit(f"Parâmetro inválido (esperado CHAVE=VALOR): '{item}'")
        mapping[key] = value
    return mapping


def parse_args():
    parser = argparse.ArgumentParser(description="Prepara as planilhas de times de cada competição.")
    parser.add_argument("--source", required=True, help="Planilha de inscrições")
    parser.add_argument("--sheet", default=0, help="Aba da planilha (padrão: a primeira)")
    parser.add_argument("--category-column", help="Coluna que define a competição de cada time")
    parser.add_argument("--category", action="append", metavar="VALOR=CÓDIGO",
                        help="Valor da coluna de categoria e o código da competição (repetível)")
    parser.add_argument("--code", help="Código da competição quando não há coluna de categoria")
    parser.add_argument("--rename", action="append", metavar="ANTIGA=NOVA", help="Renomeia uma coluna (repetível)")
    parser.add_argument("--location", help="Valor da coluna de local de prova (column_sheet_location)")
    parser.add_argument("--output", default="input/[{}] Times.xlsx",
                        help="Caminho de saída, com {} no lugar do código da competição")
    args = parser.parse_args()
    if bool(args.category_column) == bool(args.code):
        parser.error("informe --category-column (com --category) ou --code")
    if args.category_column and not args.category:
        parser.error("--category-column exige ao menos um --category")
    return args


def clean(series):
    """Remove espaços nas pontas e repetidos."""
    return series.astype(str).str.split().str.join(" ")


def save(df, code, args, institution_column):
    df = normalize_institutions(df.copy(), institution_column, f"[{code}] Times")
    out = BASE / args.output.format(code)
    df.to_excel(out, index=False)
    print(f"\nArquivo criado: {args.output.format(code)} ({len(df)} linhas)")


def main():
    args = parse_args()
    dotenv.load_dotenv(BASE / ".env")
    team_column = os.environ["column_sheet_team_name"]
    institution_column = os.environ["column_sheet_institution"]

    df = pd.read_excel(BASE / args.source, sheet_name=args.sheet)
    # Remove colunas sem cabeçalho (resumos, índices exportados etc.)
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    df = df.rename(columns=parse_mapping(args.rename))

    missing = [c for c in (team_column, institution_column, args.category_column) if c and c not in df.columns]
    if missing:
        raise SystemExit(f"Colunas não encontradas (use --rename): {missing}")

    for column in [team_column, institution_column] + ([args.category_column] if args.category_column else []):
        df[column] = clean(df[column])
    if args.location:
        df[os.environ["column_sheet_location"]] = args.location

    if args.code:
        save(df, args.code, args, institution_column)
        return

    categories = parse_mapping(args.category)
    unknown = sorted(set(df[args.category_column]) - set(categories))
    if unknown:
        print(f"\nAVISO: categorias sem código, times ignorados: {unknown}")
    for category, code in categories.items():
        save(df[df[args.category_column] == category], code, args, institution_column)


if __name__ == "__main__":
    main()
    print("\nPreparação concluída.")
