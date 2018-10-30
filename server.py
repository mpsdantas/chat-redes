from socket import *
import threading

listaDeClientesConectados = []

class ThreadConexoes (threading.Thread):
    def __init__(self, connectionSocket):
        threading.Thread.__init__(self)
        self.connectionSocket = connectionSocket

    def run(self):
        aguardaConexoes(self.connectionSocket)
      
def aguardaConexoes(connectionSocket):
    print('Novo cliente conectado. Nova Thread criada para esse cliente.')
    
    boasVindas = "Bem vindo ao chat da disciplina de redes de computadores, digite uma opção abaixo:\n1.Sala pública\n2.Sala privada\n3.Sair"
    connectionSocket.send(boasVindas.encode('utf-8'))
    

    while True:
        sentence = connectionSocket.recv(1024) # recebe dados do cliente
        sentence = sentence.decode('utf-8')
        capitalizedSentence = sentence.upper() # converte em letras maiusculas
        print ('Cliente %s enviou: %s, transformando em: %s' % (addr, sentence, capitalizedSentence))
        connectionSocket.send(capitalizedSentence.encode('utf-8')) # envia para o cliente o texto transformado
        #connectionSocket.close() # encerra o socket com o cliente
    serverSocket.close()


serverName = '' 
serverPort = 12000 
serverSocket = socket(AF_INET,SOCK_STREAM) 
serverSocket.bind((serverName,serverPort))
serverSocket.listen(1) 
print ('Servidor TCP esperando conexoes na porta %d ...' % (serverPort))
while True:
    connectionSocket, addr = serverSocket.accept() # aceita as conexoes dos clientes
    threadConexoesServidor = ThreadConexoes(connectionSocket) # Cria uma Thread para cada nova conexão.
    threadConexoesServidor.start()
