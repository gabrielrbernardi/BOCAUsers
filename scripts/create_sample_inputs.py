"""Create sample Excel input files in the project's `input/` folder.

Run:

    python scripts/create_sample_inputs.py

This will create `input/import_users.xlsx` and `input/import_preset_users.xlsx`.
"""
import os
import pandas as pd


def ensure_input_dir(path="input"):
    os.makedirs(path, exist_ok=True)
    return path


def create_subscription_example(path):
    df = pd.DataFrame([
        {"Institution": "University of Alpha", "Location": "City X", "TeamName": "Team Alpha", "Location": "Campus Alpha" },
        {"Institution": "University of Beta", "Location": "City Y", "TeamName": "Team Beta", "Location": "Campus Beta"},
    ])
    out = os.path.join(path, "sample_import_users.xlsx")
    df.to_excel(out, index=False)
    print(f"Wrote subscription example to: {out}")


def create_preset_example(path):
    df = pd.DataFrame([
        {"ID": 901, "TeamName": "Team John", "UserType": "team"},
        {"ID": 902, "TeamName": "Judge Doe", "UserType": "judge"},
        {"ID": 903, "TeamName": "Staff Smith", "UserType": "staff"},
        {"ID": 904, "TeamName": "Admin Johnson", "UserType": "admin"},
    ])
    out = os.path.join(path, "sample_import_preset_users.xlsx")
    df.to_excel(out, index=False)
    print(f"Wrote preset users example to: {out}")


def main():
    path = ensure_input_dir()
    create_subscription_example(path)
    create_preset_example(path)


if __name__ == "__main__":
    main()
