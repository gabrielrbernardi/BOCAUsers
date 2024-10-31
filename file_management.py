import pandas as pd
import string
import secrets

# input_file = "input//inscricao_mineira.xlsx"
input_file = "input//Teams.xlsx"
preset_users_file = "input//preset_users.xlsx"

column_institution = "instituicao"
column_team_name = "nome_time"
column_team_name_full = "nome_time_full"
column_username = "username"
column_password = "password"
column_id = "id"

index_begin_slice = 0
index_end_slice = 2

class FileManagement:

    def __init__(self):
        self.counter = 2000
        self.counter_ccl = 3000
        self.passwordLength = 8
        pass

    def read_subscriptions(self):
        self.subscritptions_original = pd.read_excel(input_file)

        self.subscritptions_original[column_team_name] = self.subscritptions_original[column_team_name].astype(str)

        self.sliced_subscriptions = self.subscritptions_original.iloc[:,index_begin_slice:index_end_slice]

        self.users_df = self.sliced_subscriptions

        self.users_df = self.users_df.sort_values(column_team_name)

        self.users_df = self.users_df.apply(self.iterate_lines_team, axis=1)

        # print(self.users_df.to_string())

        self.users_df = self.users_df[[column_id, column_institution, column_team_name_full, column_username, column_password]]

        return self.users_df

    def read_preset_users(self):
        self.preset_users = pd.read_excel(preset_users_file)

        self.preset_users = self.preset_users.apply(self.iterate_lines_preset, axis=1)

        return self.preset_users

    ################# ITERATION FUNCTIONS #################
    
    def iterate_lines_team(self, linha):

        if "CCL - " in linha[column_institution]:
            linha[column_id] = self.counter_ccl
            self.counter_ccl += 1

            # remove flag from ccl team name

            linha[column_team_name] = linha[column_team_name].replace("|ZZTROCAR ", "")
        else:
            linha[column_id] = self.counter
        
        linha[column_username] = "team" + str(linha[column_id])
        linha[column_password] = self.generatePassword()
        linha[column_team_name_full] = "[" + str(linha[column_institution]) + "] " + str(linha[column_team_name])
        self.counter += 1

        return linha
    
    def iterate_lines_preset(self, linha):
        linha[column_username] = linha[column_team_name]
        linha[column_password] = self.generatePassword()
        return linha
    
    ################# UTILS #################

    def generatePassword(self, _=""):
        alfabeto = string.ascii_lowercase + string.digits
        senha = "".join(secrets.choice(alfabeto) for _ in range(self.passwordLength))
        return senha