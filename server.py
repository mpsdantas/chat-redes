from socket import *
import threading
from ast import literal_eval

def enviarMensagens(clientes, nickname, mensagem):
    for clientesSockets in clientes:
        if clientesSockets['nickName'] != nickname:
            clientesSockets['socket'].send(str(mensagem).encode('utf-8'))

def enviarListaDeUsuarios(clientes, connectionSocket, nickname, addr):
    tamanho = len(clientes)
    stringUsuarios = "----------------------------------------\n"
    stringUsuarios += "Lista de usuários conectados " + str(tamanho) + ": \n"
    for clientesConectados in clientes:
        stringUsuarios += str(clientesConectados['nickName'])
        if clientesConectados['privado']:
            stringUsuarios += ' (privado)'
        stringUsuarios += '\n'
    stringUsuarios += "----------------------------------------"
    protocoloEnvioMsg = gerarProtocolo(len(stringUsuarios),addr[0].encode('utf-8'),nickname,"lista",stringUsuarios)
    connectionSocket.send(str(protocoloEnvioMsg).encode('utf-8'))

def getComando(comando):
    comandoExtraido = comando[comando.find("(")+1:comando.find(")")]
    comandoExtraido = comandoExtraido.replace("'","")
    return comandoExtraido

def gerarProtocolo(tamanhoMsg, ipDestino, nickname, comando, sentence):
    return {
            "tamanhoMsg": tamanhoMsg,
            "enderecoIpOrigem": '127.0.0.1',
            "enderecoDestino": ipDestino,
            "nickNameDoUsuario": nickname.encode('utf-8'),
            "comando": comando.encode('utf-8'),
            "dados": sentence.encode('utf-8')
        }
listaDeClientesConectados = []
serverName = '' 
serverPort = 12000 

serverSocket = socket(AF_INET,SOCK_STREAM) 
serverSocket.bind((serverName,serverPort))
serverSocket.listen(1) 

clientes = []
privados = []

print ('Servidor TCP esperando conexoes na porta %d ...' % (serverPort))

class ThreadConexoes (threading.Thread):
    def __init__(self, connectionSocket):
        threading.Thread.__init__(self)
        self.connectionSocket = connectionSocket

    def run(self):
        aguardaConexoes(self.connectionSocket)
      
def aguardaConexoes(connectionSocket):
    nickname = connectionSocket.recv(1024) # recebe dados do cliente
    nickname = nickname.decode('utf-8')
    novoCliente = {
        'nickName': nickname,
        'socket': connectionSocket,
        'privado': False
    }
    clientes.append(novoCliente)
    
    connectionSocket.send(addr[0].encode('utf-8'))

    stringEntrada = nickname + " entrou..."
    print(stringEntrada)

    protocoloEnvioMsg = gerarProtocolo(len(stringEntrada),addr[0].encode('utf-8'),nickname,"",stringEntrada)

    for clientesSockets in clientes:
        clientesSockets['socket'].send(str(protocoloEnvioMsg).encode('utf-8'))

    while True:
        try:
            # Recebe os dados do cliente
            sentence = connectionSocket.recv(1024)
            sentence = sentence.decode('utf-8')

            # Convertendo a string para um dicionario
            protocoloRecebido = literal_eval(sentence)

            if(protocoloRecebido['comando']!=""):
                stringComando = protocoloRecebido['comando'].decode('utf-8')
                if stringComando.find('nome')==0:
                    novoNickName = getComando(stringComando)
                    novoNickNameMsg = nickname + " mudou para " + novoNickName
                    for clientesConectados in clientes:
                        if str(clientesConectados['nickName']) == str(protocoloRecebido['nickNameDoUsuario'].decode('utf-8')):
                            clientesConectados['nickName'] = novoNickName
                            nickname = novoNickName

                    protocoloEnvioMsg = gerarProtocolo(len(novoNickNameMsg),addr[0].encode('utf-8'),nickname,"nome",novoNickNameMsg)

                    enviarMensagens(clientes, nickname, protocoloEnvioMsg)

                if stringComando.find('privado')==0:
                    nickNamePrivado = getComando(stringComando)
                    contador = 0
                    usuarioEnviarPrivado = -1
                    for clientesConectados in clientes:
                        if str(clientesConectados['nickName']) == str(nickNamePrivado):
                           usuarioEnviarPrivado = contador 
                        contador = contador + 1
                    if usuarioEnviarPrivado != -1:
                        stringPrivado = nickname + " deseja iniciar uma sala privada com você, aceita: (digite sim para aceitar)"

                        protocoloEnvioMsg = gerarProtocolo(len(stringPrivado),addr[0].encode('utf-8'),nickname,"privado",stringPrivado)

                        clientes[usuarioEnviarPrivado]['socket'].send(protocoloEnvioMsg)
                    else:
                        connectionSocket.send("NickName não foi encontrado")

                if protocoloRecebido['comando'].decode('utf-8')=='lista()':
                    enviarListaDeUsuarios(clientes, connectionSocket, nickname, addr)

                if protocoloRecebido['comando'].decode('utf-8')=='sair()':
                    usuarioApagar = -1
                    contador = 0
                    for clientesConectados in clientes:
                        if str(clientesConectados['nickName']) == str(protocoloRecebido['nickNameDoUsuario'].decode('utf-8')):
                            usuarioApagar = contador
                        contador = contador + 1
                    if usuarioApagar != -1:
                        print(nickname + ' saiu...')
                        mensagemSaida = nickname + " saiu..."
                        protocoloEnvioMsg = gerarProtocolo(len(mensagemSaida),addr[0].encode('utf-8'),nickname,"sair",mensagemSaida)
                        connectionSocket.send(str(protocoloEnvioMsg).encode('utf8'))
                        enviarMensagens(clientes, nickname, protocoloEnvioMsg)

                        clientes.pop(usuarioApagar)
                        connectionSocket.close()   
                   
            else:
                enviarMensagem = nickname + ": " + protocoloRecebido['dados'].decode('utf-8')
                
                protocoloEnvio = gerarProtocolo(len(enviarMensagem),str(protocoloRecebido['enderecoIpOrigem']),nickname,"",enviarMensagem);
                
                enviarMensagens(clientes, nickname, protocoloEnvio)
            
        except:
            connectionSocket.close()
            break
    
while True:
    try:
        connectionSocket, addr = serverSocket.accept() # aceita as conexoes dos clientes
        threadConexoesServidor = ThreadConexoes(connectionSocket) # Cria uma Thread para cada nova conexão.
        threadConexoesServidor.start()
    except:
         serverSocket.close()




