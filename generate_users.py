import pandas as pd

all_multi_login = True

class GenerateUsers:
    # def __init__(self):
    #     pass
        
    def __init__(self, users_dataframe : pd, preset_users_dataframe:pd, output_path:str, output_users_file_text:str, output_preset_users_file_text:str, output_all_users_file_spreadsheet:str, column_sheet_institution:str, column_sheet_team_name:str, column_sheet_team_name_full:str, column_sheet_username:str, column_sheet_password:str, column_sheet_id:str, column_sheet_user_type:str, output_preset_users_file_spreadsheet:str):
        self.users_dataframe = users_dataframe
        self.preset_users_dataframe = preset_users_dataframe
        self.output_path = output_path
        self.output_users_file_text = output_users_file_text
        self.output_preset_users_file_text = output_preset_users_file_text
        self.output_all_users_file_spreadsheet = output_all_users_file_spreadsheet
        self.column_sheet_institution = column_sheet_institution
        self.column_sheet_team_name = column_sheet_team_name
        self.column_sheet_team_name_full = column_sheet_team_name_full
        self.column_sheet_username = column_sheet_username
        self.column_sheet_password = column_sheet_password
        self.column_sheet_id = column_sheet_id
        self.column_sheet_user_type = column_sheet_user_type
        self.output_preset_users_file_spreadsheet = output_preset_users_file_spreadsheet


    def generate_output(self):
        self.f_output = open(self.output_path + "//" + self.output_users_file_text, "w", encoding='utf-8')

        self.f_output.write("[user]" + "\n")

        self.users_dataframe = self.users_dataframe.apply(self.print_users, axis=1)

        self.f_output = open(self.output_path + "//" + self.output_preset_users_file_text, "w", encoding='utf-8')
        self.f_output.write("[user]" + "\n")
        self.preset_users_dataframe = self.preset_users_dataframe.apply(self.print_users, axis=1)
    
    def print_users(self, linha):
        self.f_output.write(f"usernumber={linha[self.column_sheet_id]}" + "\n")
        self.f_output.write(f"usersitenumber=1" + "\n")
        
        if not "username" in linha:
            self.f_output.write(f"username={linha[self.column_sheet_team_name]}" + "\n")
        else:
            self.f_output.write(f"username={linha[self.column_sheet_username]}" + "\n")

        self.f_output.write(f"userpassword={linha[self.column_sheet_password]}" + "\n")
        
        if self.column_sheet_user_type in linha:
            usertype = linha[self.column_sheet_user_type]
            
            if linha[self.column_sheet_user_type] != "team":
                user_multi_login = "t"
            else:
                user_multi_login = "f"
        else:
            # default option for users
            usertype = "team"
            if all_multi_login == True:
                user_multi_login = "t"
            else:
                user_multi_login = "f"

        self.f_output.write(f"usertype={usertype}" + "\n")
        
        if self.column_sheet_team_name_full in linha:
            team_name = self.column_sheet_team_name_full
        else:
            team_name = self.column_sheet_team_name
        
        self.f_output.write(f"userfullname={linha[team_name]}" + "\n")
        self.f_output.write(f"userdesc={linha[team_name]}" + "\n")
        self.f_output.write(f"usermultilogin={user_multi_login}" + "\n")
        self.f_output.write(f"userchangepassword=f" + "\n")
        self.f_output.write(f"userenabled=t" + "\n")

        self.f_output.write("\n")

        return linha

    def generate_spreadsheet(self):

        # Filter columns

        self.preset_users_dataframe = self.preset_users_dataframe[[self.column_sheet_id, self.column_sheet_team_name, self.column_sheet_username, self.column_sheet_password]]

        with pd.ExcelWriter(self.output_path + "//" + self.output_all_users_file_spreadsheet) as writer:
            self.users_dataframe.to_excel(writer, sheet_name="Teams")  
            self.preset_users_dataframe.to_excel(writer, sheet_name="Other")
        
        # with pd.ExcelWriter(self.output_path + "//" + self.output_all_users_file_spreadsheet) as writer:
        # users_df.to_excel(output_file, index=False)

        self.preset_users_dataframe.to_excel(f"{self.output_path}//{self.output_preset_users_file_spreadsheet}", index=False)