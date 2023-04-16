import smtplib
import logging
import traceback
import pandas as pd
import time

logging.basicConfig(filename="logs.log", format='%(levelname)s - %(asctime)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s', datefmt='%d/%m/%Y %H:%M:%S %z', level=logging.DEBUG)

establishingConnectionMessage = "Efetuando conexao em: "
successfulConnectionMessage = "Conexao Sucedida!"
connectedUserMessage = "Usuario Conectado!"
promptPasswordMessage = "Digite a senha: "
authenticationErrorMessage = "Erro de autenticacao do usuario no servidor. Usuario ou senha incorretos."
errorMessage = " ERRO "

senderEmail = "gabriel.bernardi@ufu.br"
password = ""

def sendEmail():
    port = 587  # Porta para conexao SSL, definida pelo servidor POP Checkup
    smtpServer = "smtp.office365.com" #servidor de saida de emails
    try:
        logging.info(establishingConnectionMessage + smtpServer + ":" + str(port))
        with smtplib.SMTP(smtpServer, port) as server:
            server.starttls()

            # dataFrameUsers = pd.read_excel("C:\\Users\\gabri\\Documentos\\github\\ScriptInscricaoBOCA\\newVersion\\output\\resultado - Copy.xlsx")
            dataFrameUsers = pd.read_excel("C:\\Users\\gabri\\Documentos\\github\\ScriptInscricaoBOCA\\newVersion\\output\\resultado.xlsx")
            dataFrameUsers = dataFrameUsers.loc[(dataFrameUsers["Email"]).isnull() == False]
            contador = 0
            for idx, x in dataFrameUsers.iterrows():
                print(x["Email"], x["username"], x["userfullname"])
                print(str(contador+1) + "/" + str(len(dataFrameUsers)))
                # print(x["Email"], x["username"], x["Senha"], x["userfullname"])

                message = """\
Subject: Credenciais para os Contests de Treinamento da Maratona de Programação

Olá! Bom dia, time {userfullname}!

Segue os dados para seu time acessar os contests de treinamento.

https://maratona.facom.ufu.br/
Name: {username}
Password: {password}

IMPORTANTE 1: O usuário e senha será o mesmo para todos contests.

IMPORTANTE 2: O acesso estará liberado a partir de 09/03/2023, às 07:00h para testes. A partir do dia 11/03/2023, os acessos serão feitos de forma definitiva.

IMPORTANTE 3: Se tiver alteração no IP o login é bloqueado. Sabemos que isso pode ocorrer em situações diversas, exemplo: reconexão de Internet. Caso ocorra o bloqueio, favor solicitar o desbloqueio por email para gabriel.bernardi@ufu.br com cópia para joaohs@ufu.br. Tentaremos liberar o quanto antes.

IMPORTANTE 4: Esse email foi enviado para o endereço cadastrado no formulário de inscrição (times com mais de 1 inscrição, foi considerada apenas uma). Favor repassar estas informações para os participantes do seu time.


No drive do treinamento há informações sobre os tópicos, datas e horários.
Link: https://bit.ly/aularpfacom

Esperamos que goste dos contests e que estes contribuam para estudar, com diversão!


---
Cordialmente,
Gabriel Ribeiro Bernardi
João Henrique de Souza Pereira
Universidade Federal de Uberlândia - UFU
Faculdade de Computação
joaohs@ufu.br
www.facom.ufu.br
""".format(username=x["username"], password=x["Senha"], userfullname=x["userfullname"])
                logging.info(successfulConnectionMessage)
                # server.starttls(context=context)
                logging.info("Usuario: " + senderEmail)
                if contador % 6 == 0:
                    server.login(senderEmail, password)
                logging.info(connectedUserMessage)
                logging.info("Enviando email para: " + x["Email"])
                # server.sendmail(senderEmail, x["Email"], message.encode("utf-8"))
                server.sendmail(senderEmail, x["Email"], message.encode("utf-8"))
                # time.sleep(2)
                contador += 1
    except smtplib.SMTPAuthenticationError:
        logging.error(authenticationErrorMessage)
        print(traceback.format_exc())
        return [False, authenticationErrorMessage]
    
    except:
        print(traceback.format_exc())
        logging.error("Erro")

sendEmail()