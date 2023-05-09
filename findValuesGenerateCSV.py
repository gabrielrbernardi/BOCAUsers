import pandas as pd
from configparser import ConfigParser
from datetime import datetime

from dataTreatment import DataTreatment

class Main():
    def __init__(self):
        self.dt = DataTreatment()
        self.readConfigFile()
        self.readCsv()
        self.findValues()
        self.writeFile()

    def readConfigFile(self):
        self.parser = ConfigParser()
        self.parser.read("C:\\Users\\gabri\\Documentos\\github\\BOCAUsers\\fileData.ini")

        self.filteredColumns = []

        db = {}
        if self.parser.has_section("fileTransformingScript"):
            params = self.parser.items("fileTransformingScript")
            for param in params:
                db[param[0]] = param[1]

            self.csvInputPath = db["csvinscricaocaminho"]
            self.csvInputFile = db["csvinscricao"]
            self.pageGeneralUsers = db["paginausuariosgerais"]
            self.pageSelectedUsers = db["paginausuariosselecionados"]
            self.csvOutputFile = db["saidacsvtransformado"]

            self.allNamesColumn = db["colunanometodos"]
            self.selectedNamesColumn = db["colunanomeselecionados"]
        
        if self.parser.has_section("filePaths"):
            params = self.parser.items("filePaths")
            for param in params:
                db[param[0]] = param[1]
            
            self.emailColumn = db["csvemailcoluna"]
            self.nameColumn = db["csvnomecoluna"]
            self.levelColumn = db["csvnivelcoluna"]
            self.birthColumn = db["csvnascimentocoluna"]

            self.filteredColumns.append(self.nameColumn)
            self.filteredColumns.append(self.emailColumn)
            self.filteredColumns.append(self.birthColumn)
            self.filteredColumns.append(self.levelColumn)
           
    def readCsv(self):
        #Leitura do arquivo com todas as inscricoes (inscricoes normais juntamente com lista de espera)
        self.dataFrameAllCompetitors = pd.read_excel(self.csvInputPath + self.csvInputFile, self.pageGeneralUsers)
        #Leitura dos competidores selecionados para participar da competicao
        self.dataFrameSelectedCompetitors = pd.read_excel(self.csvInputPath + self.csvInputFile, self.pageSelectedUsers)

    def findValues(self):
        self.dataFrameSelectedCompetitors = self.dataFrameSelectedCompetitors.apply(self.verificaLinha,axis=1)
        self.dataFrameSelectedCompetitors = self.dataFrameSelectedCompetitors.rename({"Nível": "Nivel"}, axis=1)

        self.dataFrameSelectedCompetitors = self.dataFrameSelectedCompetitors.loc[:, self.filteredColumns]

    def writeFile(self):
        #Escrita dos valores em arquivo com formato utilizado para script de geracao de usuarios
        self.dataFrameSelectedCompetitors.to_csv(self.csvInputPath+self.csvOutputFile, index=False)
        
    def verificaLinha(self, linha):
        #Consolida valores para escrita em arquivo de saida
        resultado = self.dataFrameAllCompetitors[(self.dataFrameAllCompetitors[self.allNamesColumn] == linha[self.selectedNamesColumn]) | 
                                                 (self.dataFrameAllCompetitors[self.allNamesColumn] == linha[self.selectedNamesColumn].title()) | 
                                                 (self.dataFrameAllCompetitors[self.allNamesColumn] == self.dt.clearSpecialCharacters(linha[self.selectedNamesColumn].upper()))
                                                 ]
        if len(resultado) > 1:
            resultado = resultado.head(1)
        linha["Endereco de e-mail"] = resultado["Endereco de e-mail"].to_string(index=False)
        linha["Escolaridade"] = resultado["Escolaridade"].to_string(index=False)

        birthDate = datetime.strptime(resultado["Data de nascimento"].to_string(index=False), "%Y-%m-%d")
        linha["Data de nascimento"] = birthDate
        linha["Nome completo:"] = resultado[self.allNamesColumn].to_string(index=False)
        return linha

main = Main()