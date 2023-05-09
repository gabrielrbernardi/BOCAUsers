import pandas as pd
from configparser import ConfigParser
from dataTreatment import DataTreatment
from generateUsersBoca import UsersBoca

class Main():
    def __init__(self):
        self.passwordLength = 8
        pd.options.mode.chained_assignment = None
        parser = ConfigParser()
        parser.read("C:\\Users\\gabri\\Documentos\\github\\BOCAUsers\\fileData.ini")
        # parser.read("C:\\gabriel\\github\\ScriptInscricaoBOCA\\newVersion\\fileData.ini")

        self.dt = DataTreatment(parser)

        self.dataframePresetUsers = self.dt.readFiles()
        self.classes = self.dt.filterData()
            
        #filtering preset users dataframe
        self.dataframePresetUsersAdmin = self.dataframePresetUsers[(self.dataframePresetUsers["usertype"] == "admin") | (self.dataframePresetUsers["usertype"] == "judge")]
        self.dataframePresetUsers = self.dataframePresetUsers[(self.dataframePresetUsers["usertype"] != "admin") & (self.dataframePresetUsers["usertype"] != "judge")]
        # self.dataframePresetUsersAdmin = self.dataframePresetUsers[(self.dataframePresetUsers["usertype"] == "admin")]
        self.dataframePresetUsers = self.dataframePresetUsers[(self.dataframePresetUsers["usertype"] != "admin")]
        self.dataframePresetUsers["Senha"] = self.dataframePresetUsers["userfullname"].apply(self.dt.generatePassword)
        self.classes.append(self.dataframePresetUsers)
        self.dataframePresetUsersAdmin["Senha"] = self.dataframePresetUsersAdmin["usertype"].apply(self.checkPassword)

        self.dataframePresetUsersAdminCopy = self.dataframePresetUsersAdmin.copy()

        self.dt.dataframeInscricao = self.dt.dataframeInscricao.rename({self.dt.csvNameColumn: "Nome"}, axis=1)
        self.dt.dataframeInscricao = self.dt.dataframeInscricao.apply(self.dt.clearSpecialCharacters)
        
        self.dt.dataframeInscricao["Nome"] = self.dt.dataframeInscricao["Nome"].apply(self.dt.clearSpecialCharacters)
        # self.dt.dataframeInscricao = self.dt.dataframeInscricao.set_index("Nome")
        # print(self.dt.dataframeInscricao)
        self.dataframePresetUsersAdmin = pd.concat([self.dataframePresetUsersAdmin, self.dataframePresetUsers])
        GUB = UsersBoca(outputFileUsers=self.dt.returnUsersBocaFile(), dataframeCommonUsers=self.dt.dataframeInscricao, dataframeRestrictedUsers=self.dataframePresetUsersAdmin, csvNameColumn=self.dt.csvNameColumn)
        GUB.generateImportUsers()
        GUB.writeOutputImportFile()

        with pd.ExcelWriter(self.dt.outputPath+self.dt.outputGeneralFile) as writter:
            for idx, x in enumerate(self.classes):
                pageValue = ""
                if idx >= len(self.dt.classNames):
                    pageValue = "Staff-Score"
                else:
                    pageValue = self.dt.classNames[idx]
                x.to_excel(writter, pageValue, index=False)
            self.dataframePresetUsersAdminCopy.apply(self.clearAdminExcel, axis=1)
            self.dataframePresetUsersAdminCopy.to_excel(writter, "RESTRITO (NAO IMPRIMIR)", index=False)


        print("Quantidade atual: " + str(self.dt.subscriptionsQuantity))
        print("Quantidade maxima: " + str(self.dt.subscriptionsMax))
        print("Vagas Preenchidas: " + str(round(self.dt.subscriptionsQuantity / int(self.dt.subscriptionsMax) * 100, 1)) + "%")

    def clearAdminExcel(self, linha):
        if(linha["usertype"] == "admin"):
            linha["Senha"] = ""
        return linha

    def checkPassword(self, val):
        if val == "admin":
            return self.dt.adPass
        else:
            return self.dt.generatePassword()
        # alfabeto = string.ascii_lowercase + string.digits
        # senha = "".join(secrets.choice(alfabeto) for _ in range(self.passwordLength))
        # return senha

main = Main()
