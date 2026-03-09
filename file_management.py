import pandas as pd
import string
import secrets

class FileManagement:
    def __init__(self, input_path, output_path, input_files, preset_users_file, competition_code, competition_codes, counters, output_all_users_file_spreadsheet, column_sheet_institution, column_sheet_team_name, column_sheet_team_name_full, column_sheet_location, column_sheet_username, column_sheet_password, column_sheet_id, column_sheet_user_type):
        self.input_path = input_path
        self.input_files = input_files
        self.preset_users_file = preset_users_file
        self.competition_code = competition_code  # Código da competição principal
        self.competition_codes = competition_codes  # Lista de códigos de competição para cada arquivo
        self.counters = counters  # Lista de contadores para ID
        self.output_path = output_path
        self.output_all_users_file_spreadsheet = output_all_users_file_spreadsheet
        self.column_sheet_institution = column_sheet_institution
        self.column_sheet_team_name = column_sheet_team_name
        self.column_sheet_team_name_full = column_sheet_team_name_full
        self.column_sheet_location = column_sheet_location
        self.column_sheet_username = column_sheet_username
        self.column_sheet_password = column_sheet_password
        self.column_sheet_id = column_sheet_id
        self.column_sheet_user_type = column_sheet_user_type
        self.passwordLength = 8

    def read_subscriptions(self):
        all_users = []
        for idx, input_file in enumerate(self.input_files):
            competition_code = self.competition_codes[idx] if idx < len(self.competition_codes) else self.competition_codes[-1]
            counter = self.counters[idx] if idx < len(self.counters) else self.counters[-1]
            user_number = 1  # Inicia o contador do username
            
            subscritptions_original = pd.read_excel(self.input_path + "//" + input_file)
            # subscritptions_original[column_team_name] = subscritptions_original[column_team_name].astype(str).str.title()
            subscritptions_original[self.column_sheet_team_name] = subscritptions_original[self.column_sheet_team_name].astype(str)
            print(subscritptions_original[self.column_sheet_team_name])
            sliced_subscriptions = subscritptions_original[[self.column_sheet_institution, self.column_sheet_location, self.column_sheet_team_name]].copy()
            
            # Adiciona colunas necessárias antes de processar
            sliced_subscriptions[self.column_sheet_id] = None  # Adiciona ID para controle interno
            sliced_subscriptions[self.column_sheet_username] = None
            sliced_subscriptions[self.column_sheet_password] = None
            sliced_subscriptions[self.column_sheet_team_name_full] = "[" + sliced_subscriptions[self.column_sheet_institution] + "] " + sliced_subscriptions[self.column_sheet_team_name]
            
            users_df = sliced_subscriptions.sort_values(self.column_sheet_team_name)
            
            def process_row(row):
                nonlocal counter, user_number
                row[self.column_sheet_id] = counter  # Mantém o ID para controle interno
                row[self.column_sheet_username] = f"team{self.competition_code}{competition_code}{user_number:03d}"  # Formato team+competition_code+3 dígitos
                row[self.column_sheet_password] = self.generatePassword()
                counter += 1
                user_number += 1
                return row
            
            users_df = users_df.apply(process_row, axis=1)
            
            all_users.append(users_df)

            # Remover a coluna "id" antes de salvar
            users_df = users_df[[self.column_sheet_team_name_full, self.column_sheet_institution, self.column_sheet_username, self.column_sheet_password]]
            
            output_file = f"{self.output_path}//users_{self.competition_code}{competition_code}.xlsx"
            users_df.to_excel(output_file, index=False)
            print(f"Arquivo salvo: {output_file}")

        all_users_df = pd.concat(all_users, ignore_index=True)

        output_file = f"{self.output_path}//{self.output_all_users_file_spreadsheet}"
        all_users_df.to_excel(output_file, index=False)

        return all_users_df
    
    def read_preset_users(self):
        preset_users = pd.read_excel(self.preset_users_file)
        preset_users[self.column_sheet_username] = preset_users[self.column_sheet_team_name]
        preset_users[self.column_sheet_password] = preset_users.apply(lambda row: self.generatePassword(), axis=1)
        return preset_users

    def generatePassword(self):
        alfabeto = string.ascii_lowercase + string.digits
        return "".join(secrets.choice(alfabeto) for _ in range(self.passwordLength))

