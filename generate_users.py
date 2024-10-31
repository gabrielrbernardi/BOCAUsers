import pandas as pd

output_users_file_text = "output/import_users.txt"
output_users_file_spreadsheet = "output/all_users.xlsx"

column_institution = "instituicao"
column_team_name = "nome_time"
column_team_name_full = "nome_time_full"
column_username = "username"
column_password = "password"
column_id = "id"
column_user_type = "tipo_time"

class GenerateUsers:        
    def __init__(self, users_dataframe : pd, preset_users_dataframe:pd):
        self.users_dataframe = users_dataframe
        self.preset_users_dataframe = preset_users_dataframe

    def generate_output(self):
        self.f_output = open(output_users_file_text, "w", encoding='utf-8')

        self.f_output.write("[user]" + "\n")

        self.users_dataframe = self.users_dataframe.apply(self.print_users, axis=1)
        self.preset_users_dataframe = self.preset_users_dataframe.apply(self.print_users, axis=1)
    
    def print_users(self, linha):
        self.f_output.write(f"usernumber={linha[column_id]}" + "\n")
        self.f_output.write(f"usersitenumber=1" + "\n")
        
        if not "username" in linha:
            self.f_output.write(f"username={linha[column_team_name]}" + "\n")
        else:
            self.f_output.write(f"username={linha[column_username]}" + "\n")

        self.f_output.write(f"userpassword={linha[column_password]}" + "\n")
        
        if "tipo_time" in linha:
            usertype = linha[column_user_type]
            
            if linha["tipo_time"] != "team":
                user_multi_login = "t"
            else:
                user_multi_login = "f"
        else:
            usertype = "team"
            user_multi_login = "f"

        self.f_output.write(f"usertype={usertype}" + "\n")
        
        if column_team_name_full in linha:
            team_name = column_team_name_full
        else:
            team_name = column_team_name
        
        self.f_output.write(f"userfullname={linha[team_name]}" + "\n")
        self.f_output.write(f"userdesc={linha[team_name]}" + "\n")
        self.f_output.write(f"usermultilogin={user_multi_login}" + "\n")
        self.f_output.write(f"userchangepassword=f" + "\n")
        self.f_output.write(f"userenabled=t" + "\n")

        self.f_output.write("\n")

        return linha

    def generate_spreadsheet(self):

        # Filter columns

        self.preset_users_dataframe = self.preset_users_dataframe[[column_id, column_team_name, column_username, column_password]]


        with pd.ExcelWriter(output_users_file_spreadsheet) as writer:
            self.users_dataframe.to_excel(writer, sheet_name="Teams")  
            self.preset_users_dataframe.to_excel(writer, sheet_name="Other")  