from generate_users import GenerateUsers
from file_management import FileManagement
import dotenv
import os
import json

class Main:
    def __init__(self):
        # FM = FileManagement()

        dotenv.load_dotenv()
        
        input_path = os.getenv('input_path')
        input_files = json.loads(os.getenv('input_files'))
        competition_code = os.getenv('competition_code')
        competition_codes = json.loads(os.getenv('competition_codes'))
        counters = json.loads(os.getenv('start_id_for_competition_codes'))
        preset_users_file = os.getenv('input_path') + "//" + os.getenv('preset_users_file')
        
        output_path = os.getenv('output_path')
        output_users_file_text = os.getenv('output_users_file_text')
        output_preset_users_file_text = os.getenv('output_preset_users_file_text')
        output_all_users_file_spreadsheet = os.getenv('output_all_users_file_spreadsheet')

        # Column sheet mappings
        column_sheet_institution = os.getenv('column_sheet_institution')
        column_sheet_team_name = os.getenv('column_sheet_team_name')
        column_sheet_team_name_full = os.getenv('column_sheet_team_name_full')
        column_sheet_location = os.getenv('column_sheet_location')
        column_sheet_username = os.getenv('column_sheet_username')
        column_sheet_password = os.getenv('column_sheet_password')
        column_sheet_id = os.getenv('column_sheet_id')
        column_sheet_user_type = os.getenv('column_sheet_user_type')

        output_preset_users_file_spreadsheet = os.getenv('output_preset_users_file_spreadsheet')

        FM = FileManagement(
            input_path,
            output_path,
            input_files, 
            preset_users_file, 
            competition_code, 
            competition_codes, 
            counters,
            output_all_users_file_spreadsheet,
            column_sheet_institution,
            column_sheet_team_name,
            column_sheet_team_name_full,
            column_sheet_location,
            column_sheet_username,
            column_sheet_password,
            column_sheet_id,
            column_sheet_user_type
        )

        self.users = FM.read_subscriptions()
        print(self.users)

        self.preset_users = FM.read_preset_users()

        GU = GenerateUsers(
            self.users, self.preset_users,
            output_path,
            output_users_file_text,
            output_preset_users_file_text,
            output_all_users_file_spreadsheet,
            column_sheet_institution,
            column_sheet_team_name,
            column_sheet_team_name_full,
            column_sheet_username,
            column_sheet_password,
            column_sheet_id,
            column_sheet_user_type,
            output_preset_users_file_spreadsheet
        )

        GU.generate_output()

        GU.generate_spreadsheet()


main = Main()
