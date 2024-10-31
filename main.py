from generate_users import GenerateUsers
from file_management import FileManagement

class Main:
    def __init__(self):
        FM = FileManagement()

        self.users = FM.read_subscriptions()

        self.preset_users = FM.read_preset_users()

        GU = GenerateUsers(self.users, self.preset_users)

        GU.generate_output()

        GU.generate_spreadsheet()


main = Main()
