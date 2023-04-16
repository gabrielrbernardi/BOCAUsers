# Preparing the environment
## Dependencies
- Python
- Pandas
- Numpy
- string
- secrets
- ast
- datetime

# How it works?
There are two scripts. The first of those are `./GenerateUsersBOCA/findValuesGenerateCSV.py`. This script catch the form, that has been downloaded and prepare him for the input for the other script. It will be generated a CSV file. 
The second one (`./GenerateUsersBOCA/main.py`), uses this CSV file and generate the import-user file for BOCA (located on `./GenerateUsersBOCA/output/import-user.txt`) and generate another file, with XLSX format, that can be used for the staff, to help on locate competitors on the competition.

### Columns on `findValuesGenerateCSV.py`
The used downloaded form, for tests, have these columns: `Carimbo de data/hora,Endereco de e-mail,Nome completo:,Telefone (00)00000-0000,Data de nascimento,CPF 000.000.000-00,Endereco completo,CEP 00000-000,Escolaridade,Instituicao de Ensino,Cidade da instituicao de ensino,Camiseta baby look?,Tamanho da camiseta,Aluno em vulnerabilidade Social?,Anexe o comprovante o PIX(pdf),Anexe aqui um documento que comprove a situacao de vulnerabilidade social.`. Instead of them, the only ones that will be needed are: `Endereco de e-mail,Nome completo:,Data de nascimento,Escolaridade`.

### Columns on `main.py`
The columns that are generated by the `findValuesGenerateCSV.py` are:
`Nome completo:,Endereco de e-mail,Data de nascimento,Escolaridade`. These columns are the only ones needed for the script to work.


# The config file
The config file is used to easily manage the script. On this file (`./GenerateUsersBOCA/fileData.ini`), you'll be able to set the input directory for the competitors form and the preset users file, that will contains the basic informations that will be used for `staff`, `score`, `judge` and `admin`. It is possible too define the output directory and output file names, that will be used to store the generated contents.

## Setting the config file path
To use the config file, you need to map the path for him. This path must been inserted on `line 11`, from `./GenerateUsersBOCA/main.py` and on `line 17` on `./GenerateUsersBOCA/findValuesGenerateCSV.py`.

## Importing Download Form File
Once the form summary has been downloaded, you'll need to map the file and put the path on `fileData.ini`.
Beside, some changes are needed. 
1. First one is rename column names from CSV, to remove special characters from them. The file name must been renamed too, to remove special characters.
2. Second one is to get the column names from `Email`, `Name`, `Level/schooling` and `Brith Date` and put those names on `fileData.ini`, under the `filePaths` section.

## Date format
The date format must been setted on `./GenerateUsersBOCA/dataTreatment.py`, under the function `calculateAge`.

# Running the Scripts
To run this script, you must have python installed on your machine. This tool has been tested on Python 3.10 using Windows 11 22H2.

## Windows
To run the script on Windows, you must put this command on PowerShell
`python ./GenerateUsersBOCA/findValuesGenerateCSV.py`
`python ./GenerateUsersBOCA/main.py`

## Linux
To run these scripts on Linux, you must put this command on Bash:
`python3 ./GenerateUsersBOCA/findValuesGenerateCSV.py`
`python3 ./GenerateUsersBOCA/main.py`

# Generated Results
## Password
The password that will be used by the users, it will be generated randomly, and contains the combination of lower case letters and digits.

## Output files
Once the script has been executed, it will produce two different files. The first one is `./GenerateUsersBOCA/output/import-user.txt` that is used on BOCA to import the users to the platform. The second on is a spreadsheet `./GenerateUsersBOCA/output/resultado.xlsx` that contains all users, (separated on classes capacity, that has been setted on `fileData.ini`) and the preset users, used for staff.

### Import user file used on BOCA
The format of this file are standardized. This file contains informations of all users on the competition, including teams, staffs, scores, judges and admins. For the admin Password, this will be setted as the same for all of the admins users. This password can be configurated on `./GenerateUsersBOCA/main.py` at `line 64`.

#### Format of import-user file
```
[user]
usernumber=1
usersitenumber=1
username=team1
userpassword=jasj82ms
usertype=team
userfullname=Competitor name 01
userdesc=Competitor name 01
usermultilogin=f
userenabled=t
userchangepassword=f

usernumber=2
usersitenumber=1
username=team2
userpassword=sada452s
usertype=team
userfullname=Competitor name 02
userdesc=Competitor name 02
usermultilogin=f
userenabled=t
userchangepassword=f
...

usernumber=1153
usersitenumber=1
username=judge01
userpassword=2yop77vg
usertype=judge
userfullname=Judge01
userdesc=Judge01
usermultilogin=t
userenabled=t
userchangepassword=t
...

usernumber=1164
usersitenumber=1
username=admin01
userpassword=adminPassword
usertype=admin
userfullname=Admin01
userdesc=Admin01
usermultilogin=t
userenabled=t
userchangepassword=t
...

usernumber=1167
usersitenumber=1
username=staff01
userpassword=aa8mkny7
usertype=staff
userfullname=Staff01
userdesc=Staff01
usermultilogin=t
userenabled=t
userchangepassword=t
...

usernumber=1174
usersitenumber=1
username=score01
userpassword=bj8dkuyf
usertype=score
userfullname=Score01
userdesc=Score01
usermultilogin=t
userenabled=t
userchangepassword=t
```