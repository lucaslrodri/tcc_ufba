import socket
import time

HOST = '192.168.174.97'  # Endereco IP do computador na rede
PORT = 5005            # Porta que o Servidor esta
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (HOST, PORT)
msg = 'Ola mundo'
while True:
    sock.sendto (msg, dest)
    time.sleep(2)
sock.close()


import socket

HOST = "" #Quando vazio indica que pode receber de qualquer IP
PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
orig = (HOST, PORT)
sock.bind(orig)

while True:
    data, addr = sock.recvfrom(1024) # Tamanho do buffer, ou seja, quantidade de dados enviados em uma conexão (1024 bytes)
    print "Mensagem recebida: ", data
sock.close()