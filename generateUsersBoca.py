
class UsersBoca():
    def __init__(self, outputFileUsers, dataframeCommonUsers, dataframeRestrictedUsers, csvNameColumn):
        self.outputFileUsers = outputFileUsers
        self.dataframeCommonUsers = dataframeCommonUsers
        self.dataframeRestrictedUsers = dataframeRestrictedUsers
        self.csvNameColumn = csvNameColumn

        self.openOutputFile()

    def openOutputFile(self):
        self.f = open(self.outputFileUsers, "w")

    def teste(self):
        return self.dataframeCommonUsers

    def generateImportUsers(self):
        lista = []
        # print(self.dataframeCommonUsers)

        indice = 0
        for idx, x in self.dataframeCommonUsers.iterrows():
            lista.append("usernumber=" + str(indice + 1) + "\n")
            lista.append("usersitenumber=" + str(1) + "\n")
            lista.append("username=" + str(x["Username"]) + "\n")
            lista.append("userpassword=" + str(x["Senha"]) + "\n")
            lista.append("usertype=" + str(x["usertype"]) + "\n")
            lista.append("userfullname=" + str(x["Nome"]) + "\n")
            lista.append("userdesc=" + str(x["Nome"]) + "\n")
            lista.append("usermultilogin=" + str("f") + "\n")
            lista.append("userenabled=" + str("t") + "\n")
            lista.append("userchangepassword=" + str("f") + "\n")
            lista.append("\n")
            indice += 1
        
        for idx, x in self.dataframeRestrictedUsers.iterrows():
            lista.append("usernumber=" + str(indice + 1000) + "\n")
            lista.append("usersitenumber=" + str(1) + "\n")
            lista.append("username=" + str(x["username"]) + "\n")
            lista.append("userpassword=" + str(x["Senha"]) + "\n")
            lista.append("usertype=" + str(x["usertype"]) + "\n")
            lista.append("userfullname=" + str(x["userfullname"]) + "\n")
            lista.append("userdesc=" + str(x["userfullname"]) + "\n")
            lista.append("usermultilogin=" + str("t") + "\n")
            lista.append("userenabled=" + str("t") + "\n")
            lista.append("userchangepassword=" + str("t") + "\n")
            lista.append("\n")
            indice += 1

        self.usersList = lista
    
    def writeOutputImportFile(self):
        self.f.write("[user]\n")
        for x in self.usersList:
            # print(x)
            self.f.write(x)
        self.f.close()

        # lista.append("usersitenumber=" + users[x]["usersitenumber"] + "\n")
        # lista.append("username=" + users[x]["username"] + "\n")
        # lista.append("userpassword=" + users[x]["userpassword"] + "\n")
        # lista.append("usertype=" + users[x]["usertype"] + "\n")
        # lista.append("userfullname=" + users[x]["userfullname"] + "\n")
        # lista.append("userdesc=" + users[x]["userdesc"] + "\n")
        # lista.append("usermultilogin=" + users[x]["usermultilogin"] + "\n")
        # lista.append("userenabled=" + users[x]["userenabled"] + "\n")
        # lista.append("userchangepassword=f" + "\n")


        # usernumber=387
        # usersitenumber=1
        # username=Team387
        # userpassword=0ohuukxs
        # usertype=team
        # userfullname=Team387
        # userdesc=Team387
        # usermultilogin=f
        # userenabled=t
        # userchangepassword=f