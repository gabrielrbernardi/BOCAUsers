import pandas as pd
import numpy as np
import string
import secrets
import ast
from datetime import datetime
import math

class DataTreatment():
    def __init__(self, parser=""):
        if parser == "":
            pass
        else:
            # self.dataFrameInscricao = dataFrameInscricao
            self.parser = parser
            self.neededColumns = []
            self.usernames = []
            self.quantidadeUsernames = 0
            self.passwordLength = 8
            self.proportionListClass = []

            db = {}
            if self.parser.has_section("filePaths"):
                params = self.parser.items("filePaths")
                for param in params:
                    db[param[0]] = param[1]

                self.csvInputPath = db["csvinscricaocaminho"]
                self.csvInputFile = db["csvinscricao"]      
                self.csvPresetUsers = self.csvInputPath+db["csvpresetusers"]      
                self.csvEmailColumn = db["csvemailcoluna"]
                self.csvNameColumn = db["csvnomecoluna"]
                self.csvLevelColumn = db["csvnivelcoluna"]
                self.csvBirthColumn = db["csvnascimentocoluna"]
                self.adPass = db["adpass"]
                
                self.neededColumns.append(self.csvNameColumn)
                # self.neededColumns.append(self.csvLevelColumn)
                
                self.outputPath = db["caminhosaidaarquivos"]
                self.outputGeneralFile = db["xlsxgeralformatado"]
                self.outputBocaUsersFile = self.outputPath + db["outputbocafiletext"]
                
                self.classCapacity = ast.literal_eval(db["capacidadeturmas"])
                self.classNames = eval(db["nometurmas"])
                self.quantityMaxSubscriptions = db["quantidademaximainscricoes"]
                self.classFilled = []

    def returnUsersBocaFile(self):
        return self.outputBocaUsersFile

    def readFiles(self):
        self.csvInputFullName = self.csvInputPath + self.csvInputFile
        self.dataframeInscricao = pd.read_csv(self.csvInputFullName)
        self.dataframePresetUsers = pd.read_csv(self.csvPresetUsers, encoding = "ISO-8859-1")

        return self.dataframePresetUsers

    def filterData(self):
        #filtering subscription dataframe
        self.dataframeInscricao[self.csvNameColumn] = self.dataframeInscricao[self.csvNameColumn].str.strip()
        self.dataframeInscricao[self.csvEmailColumn] = self.dataframeInscricao[self.csvEmailColumn].str.strip()
        self.dataframeInscricao["Idade"] = self.dataframeInscricao[self.csvBirthColumn].apply(self.calculateAge)
        # self.neededColumns.append("Idade")
        self.dataframeInscricao = self.dataframeInscricao.sort_values(by=[self.csvLevelColumn,"Idade",self.csvNameColumn])
        self.dataframeInscricao["Username"] = self.dataframeInscricao[self.csvNameColumn].apply(self.generateUsername)
        self.neededColumns.append("Username")
        self.dataframeInscricao["Nome"] = self.dataframeInscricao[self.csvNameColumn].apply(self.clearSpecialCharacters)
        self.dataframeInscricao["Senha"] = self.dataframeInscricao["Username"].apply(self.generatePassword)
        self.neededColumns.append("Senha")
        self.dataframeInscricao = self.dataframeInscricao.drop_duplicates(subset=[self.csvEmailColumn])
        

        self.dataframeInscricao = self.dataframeInscricao.loc[:, self.neededColumns]
        self.dataframeInscricao["usertype"] = "team"
        self.calculateUsersPerClass()
        split_idx = np.cumsum(self.classFilled)[:-1]
        #Definicao de valor para geracao de sequencia correta
        self.quantidade = 0
        self.dataframeInscricao = self.dataframeInscricao.apply(self.generateIndex, axis=1)
        self.dataframeInscricao.reset_index(drop=True)
        self.classes = np.split(self.dataframeInscricao, split_idx)

        return self.classes
    
    
    def generateIndex(self, linha):
        self.quantidade += 1
        linha["Indice"] = self.quantidade
        return linha

    def calculateUsersPerClass(self):
        for i in self.classCapacity:
            #Calculo da proporcao em que cada sala possui em relacao a capacidade maxima
            self.proportionListClass.append(i / sum(self.classCapacity))
            
            #Calculo da quantidade de alunos, de acordo com a proporcao de preenchimento de sala
            self.classFilled.append(math.ceil(i / sum(self.classCapacity) * len(self.dataframeInscricao)))
        
        self.subscriptionsQuantity = len(self.dataframeInscricao)
        # self.subscriptionsMax = sum(self.classCapacity)
        self.subscriptionsMax = self.quantityMaxSubscriptions
    
    def clearSpecialCharacters(self, username):
        username = username.replace('á', 'a')
        username = username.replace('Á', 'A')
        username = username.replace('ã', 'a')
        username = username.replace('Ã', 'A')
        username = username.replace('â', 'a')
        username = username.replace('Â', 'A')
        username = username.replace('ª', 'a')
        username = username.replace('é', 'e')
        username = username.replace('É', 'E')
        username = username.replace('ê', 'E')
        username = username.replace('Ê', 'E')
        username = username.replace('í', 'i')
        username = username.replace('Í', 'I')
        username = username.replace('ó', 'o')
        username = username.replace('Ó', 'O')
        username = username.replace('õ', 'o')
        username = username.replace('Õ', 'o')
        username = username.replace('ô', 'o')
        username = username.replace('Ô', 'o')
        username = username.replace('ú', 'u')
        username = username.replace('Ú', 'U')
        username = username.replace('ç', 'c')
        username = username.replace('Ç', 'C')
        return username
    
    def calculateAge(self, birthDate):
        # birthDate = datetime.strptime(birthDate, "%d/%m/%Y")
        birthDate = datetime.strptime(birthDate, "%Y-%m-%d")
        today = datetime.now()
        resultado = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
        return resultado 
    
    def generateUsername(self, nome):
        nome = ("team"+str(self.quantidadeUsernames + 1))
        self.quantidadeUsernames += 1
        return nome

    def generatePassword(self, _=""):
        alfabeto = string.ascii_lowercase + string.digits
        senha = "".join(secrets.choice(alfabeto) for _ in range(self.passwordLength))
        return senha