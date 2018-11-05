from socket import *
import re, json, threading, time
from ast import literal_eval
global conectado
conectado = True 

class recebeMsg (threading.Thread):
    # redefine a funcao __init__ para aceitar a passagem parametros de entrada
    def __init__(self,clientSocket):
        threading.Thread.__init__(self)
        self.client_Socket = clientSocket
    # a funcao run() e executada por padrao por cada thread
    def run(self):
        global conectado
        while conectado:
            msg = self.client_Socket.recv(2048)
            msg = msg.decode('utf-8')
        
            # Convertendo a string para um dicionario
            protocoloRecebido = literal_eval(msg)

            print(protocoloRecebido['dados'].decode('utf-8'))

def getComando(comando):
    comandoExtraido = comando[comando.find("(")+1:comando.find(")")]
    comandoExtraido = comandoExtraido.replace("'","")
    return comandoExtraido

def getProtocolo(sentence, tamanhoMsg, ipUsuario, ipDestino, nickname):
    if sentence[0:-1]==getComando(sentence):
        return {
            "tamanhoMsg": tamanhoMsg,
            "enderecoIpOrigem": ipUsuario,
            "enderecoDestino": ipDestino,
            "nickNameDoUsuario": nickname.encode('utf-8'),
            "comando": "",
            "dados": sentence.encode('utf-8')
        }
    else:
        return {
            "tamanhoMsg": tamanhoMsg,
            "enderecoIpOrigem": ipUsuario,
            "enderecoDestino": ipDestino,
            "nickNameDoUsuario": nickname.encode('utf-8'),
            "comando": sentence.encode('utf-8'),
            "dados": ""
        }

#definicao das variaveis
serverName = 'localhost' # ip do servidor
serverPort = 12000 # porta a se conectar
clientSocket = socket(AF_INET,SOCK_STREAM) # criacao do socket TCP
clientSocket.connect((serverName, serverPort)) # conecta o socket ao servidor

#Configurando nickname
nickname = ""
while nickname == "":
    nickname = input("Por favor digite um nickname: ")

clientSocket.send(nickname.encode('utf-8'))

ipUsuario = clientSocket.recv(2048).decode('utf-8')

thread = recebeMsg(clientSocket)
thread.start()

comandoInvalido = True
comandoSelecionado = ""
try:
    while conectado:
        try:
            sentence = input()
            tamanhoMsg = len(sentence.encode('utf-8'))
            protocoloDeEnvio = getProtocolo(sentence, tamanhoMsg, ipUsuario, serverName, nickname)
            
            if sentence.find('nome')==0:
                print("você mudou seu nickname para " + getComando(sentence))
                nickname = getComando(sentence)

            clientSocket.send(str(protocoloDeEnvio).encode('utf-8')) # envia o texto para o servidor
            if protocoloDeEnvio['comando'].decode('utf-8') == "sair()":
                conectado = False
                clientSocket.close()
                break
            
        except:
            time.sleep(0.05)
finally:
    clientSocket.close



