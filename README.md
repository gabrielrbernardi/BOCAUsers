# BOCAUsers

Small utility to generate BOCA import files (text and spreadsheets) from Excel subscription lists and preset users.

## Requirements

- Python 3.8+
- pandas
- python-dotenv
- openpyxl

Install dependencies:

```bash
pip3 install -r requirements.txt
```

## Project layout

- `main.py` — entry point, reads environment variables and runs the pipeline.
- `file_management.py` — reads input Excel files and generates user accounts.
- `generate_users.py` — writes BOCA-format text files and exports spreadsheets.
- `input/` — put input Excel files here.
- `output/` — generated files are written here.

## .env configuration

Create a `.env` file in the project root with the following keys (example values shown). A sample can be found at `.env.example`:

```
input_path="input"
input_files=["import_users.xlsx"]
competition_code="max"
competition_codes=["min"]
start_id_for_competition_codes=[1001]
preset_users_file="import_preset_users.xlsx"

output_path="output"
output_users_file_text="users.txt"
output_preset_users_file_text="preset_users.txt"
output_all_users_file_spreadsheet="all_users.xlsx"
output_preset_users_file_spreadsheet="preset_other.xlsx"

column_sheet_institution="Institution"
column_sheet_team_name="TeamName"
column_sheet_team_name_full="TeamName"
column_sheet_location="Location"
column_sheet_username="Username"
column_sheet_password="Password"
column_sheet_id="ID"
column_sheet_user_type="UserType"
```

Notes:
- Generate sample input Excel files into `input/` by running `python scripts/create_sample_inputs.py`.
- `.env.example` has been added; copy it to `.env` and edit values.
- `input_files`, `competition_codes` and `start_id_for_competition_codes` must be valid JSON arrays (use the exact syntax shown).
- Paths can be relative (recommended for portability) or absolute.


## Input Excel format

1) Subscriptions (one or more files defined in `input_files`)

- The subscription Excel files must include the columns mapped by the `column_sheet_*` env vars. For example, if `column_sheet_institution=Institution` and `column_sheet_team_name=TeamName`, your sheet should have columns named `Institution`, `Location`, and `TeamName`.
- Minimal example columns and rows (shown as a table):

| Institution | Location | TeamName |
|-------------|----------|----------|
| School A    | City X   | Team Alpha |
| School B    | City Y   | Team Beta  |

2) Preset users file

- The preset users Excel file (set via `preset_users_file`) should contain at least the team name column (mapped by `column_sheet_team_name`) and the type of this team (e.g. `admin`, `judge`, `staff`, `score` or `team`). If you want to keep specific IDs include the ID column (`column_sheet_id`). The script will generate passwords for preset users automatically.

Example columns:

| ID  | TeamName      | UserType           |
|-----|---------------|--------------------|
| 901 | Team John     | team               |
| 902 | Judge Doe     | judge              |
| 903 | Staff Smith   | staff              |
| 904 | Admin Johnson | admin              |

## Run

Make sure your `.env` is configured and input files are in `input/`, then run:

```bash
python main.py
```

This will:
- Read each Excel file listed in `input_files`.
- Generate per-competition XLSX files `output/users_<competition>.xlsx`.
- Produce a consolidated spreadsheet (`output_all_users_file_spreadsheet`).
- Write BOCA `[user]` text files to `output/` as configured.

## Output

- Text files: BOCA-format `[user]` entries (see `output_users_file_text`, `output_preset_users_file_text`).
- Spreadsheets: combined and per-competition Excel files as configured.

## Troubleshooting

- If Excel read/write fails, ensure `openpyxl` is installed.
- If environment variables aren't loaded, confirm `.env` is in the project root and keys match names in `main.py`.
- If column names mismatch, update the `column_sheet_*` variables in `.env` to match your Excel headers.

