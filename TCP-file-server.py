#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import os
import time

server_Dowload_Upload_Dir = "ServerFTP_TCP_UPLOADandDOWLOAD" # nome do Diretorio de onde o servidor vai buscar




def encontrar_pasta(caminho):    #encontrar a pasta da Variavel serve_Dowload_Upload_Dir 
    caminho_atual = os.getcwd() # pegando o caminho atual onde foi executado
    for raiz, diretorios, arquivos in os.walk(caminho_atual): # andando pelo caminho
        for diretorio in diretorios:  # para cada diretorio dentro diretorios onde foi dado o caminho
            if caminho in diretorio:     # se o nome da variavel estiver no diretorio
                return raiz+"/"+diretorio   # retorna   o caminho + /diretorio


# esse codigo foi mais especificado no UDP-file-Cliente.py
def Get_Arquive_And_Legth_Json():  # criando "json" para enviar ao cliente    Basicamente Mesma função do cliente
    while True: #loop de while True
        try:    # tente        
            arquivos_Locais = os.listdir(encontrar_pasta(server_Dowload_Upload_Dir)) # caminho onde deve ser executado 
            arquivos_Json = {} #lista vazia para json   
            for arquivo in arquivos_Locais:  # for na lista gerada por Listdir
                tamanho = os.path.getsize(encontrar_pasta(server_Dowload_Upload_Dir)+"/"+arquivo) # pegando tamanho
                arquivos_Json[arquivo]=tamanho # adicionando ao dicionario arquivo:tamanho
            return arquivos_Json #retornando a Lista Json para enviar ao cliente as possibilidades de dowloads
        except PermissionError as e:
            print("erro de permisão")
            break
        except FileNotFoundError as e:
            atual = os.getcwd()
            os.makedirs(atual+"/Server_TCP_Dowload_Updload/"+server_Dowload_Upload_Dir)
            print("Uma pasta Para Dowloads do Servidor foi Criada por favor verifique!")
        except Exception as e:
            print("Erro desconhecido", e)
            break



# Função continua sendo a mesma do udp-file-cliente.py  apenas mudando o nome do diretorio abaixo 
def Ler_arquivo(nome_arquivo):
    caminho = encontrar_pasta(server_Dowload_Upload_Dir)+"/"+nome_arquivo # Trocada o nome da variavel de diretorio
    try:
        with open(caminho, "rb") as arquivo:
            read = arquivo.readlines()
        read = b"".join(read)
        return read
    except PermissionError as e:
        print("erro de permisão",e)
    except FileNotFoundError as e:
        print("Arquivo não encontrado!")
    except Exception as e:
        print("Erro desconhecido", e)

def Criar_Arquivo(nome_arquivo,conteudo):
    try:
        caminho = encontrar_pasta(server_Dowload_Upload_Dir)+"/"+nome_arquivo # Trocada o nome da variavel de diretorio
        fd = open(caminho, "wb")
        fd.write(conteudo)
        fd.close()
    except:
        atual = os.getcwd()
        novo_caminho = atual+"Q4/Server_TCP_Dowload_Updload/"+server_Dowload_Upload_Dir    # Trocada o nome da variavel de diretorio
        os.makedirs(novo_caminho)
        fd = open(encontrar_pasta(server_Dowload_Upload_Dir)+"/"+nome_arquivo, "wb")  # Trocada o nome da variavel de diretorio
        fd.write(conteudo)
        fd.close()




# Servidor de TCP 
INTERFACE = '0.0.0.0'# ip loop back
PORT = 12345   # porta aleatoria
buffer = 1024
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((INTERFACE, PORT))#ligando porta
sock.listen(1)  # ouvindo apenas 1 conexão
conect, cliente = sock.accept()#aceitando conexão

print ("Escutando em ...", (INTERFACE, PORT))






while True:
    msg = conect.recv(buffer)  # recebendo uma msg apos conect 

    if msg == b"LS&":  # se receber os 3 Bit com o caractere LS& 
        lista = Get_Arquive_And_Legth_Json() #cria um dicionario com nome : tamanho dos arquivos da pasta passada
        send_leng = conect.send(str(len(str(lista))).encode()) # envia ao servidor o tamanho Do dicionario para enviar 
        time.sleep(0.3) # sleep 0.3 
        if send_leng: # se enviado o tamanho do dicionario que vem 
            time.sleep(0.3) #sleep 
            resp = conect.send(str(lista).encode())#enviando a lista em String codificada 
            print("a Lista de arquivos enviada!") # print para identifica o sucesso da operação
    if msg == b"CP&": # se receber os 3 Bit com o caractere CP&
        enviar = False  #False ate verificar se o arquivo existe
        while enviar == False: # repetir enquando o processo for falso
            Arquivo_para_Baixar = conect.recv(buffer) # recebendo o nome do arquivo para baixar 
            comparation = Get_Arquive_And_Legth_Json() # pegando a lista de arquivos na pasta
            if Arquivo_para_Baixar.decode() in comparation.keys(): # analise se o Arquivo exite dento da pasta se existir
                size = comparation[Arquivo_para_Baixar.decode()] #pegando o tamanho do arquivo do arquivo dentro do dicionario para enviar ao client
                conect.send(b"200") # enviar codigo"bit" 200 se achou dentro da pasta :)
                time.sleep(0.3)   # sleep 
                conect.send(str(size).encode()) # enviando tamanho total do arquivo para o servidor começar a escutar e saber quandos bytes serão enviados
                time.sleep(0.3) # sleep
                enviar_arquivo = conect.send(Ler_arquivo(Arquivo_para_Baixar.decode())) # função para ler e retorna bits concatenados e envia
                print(f"# {Arquivo_para_Baixar.decode()} size:{enviar_arquivo} bytes, send to {cliente[0]}") #msg servidor indicando o envio
                enviar = True # liberando while confirmando a existencia do arquivo dentro da pasta e liberando o loop
            elif Arquivo_para_Baixar == b"BREAK": # se no client for digitado para sair aqui deve sair do loop para se o cliente digitar 2 para sair
                break   # quebrando loop               não acontecer de receber mensagem e não saber tratar 
            else:
                conect.send(b"404") #envia codigo"bit" 404 indicando arquivo não encontrado e volta ao inicio
                print(f" {cliente[0]} try make Dowload ${Arquivo_para_Baixar.decode()}, file not found!") #retorno para visualizar no serve
    if msg == b"POST&": # recebendo POST& significa que o cliente pretende fazer um upload na pasta do server
        size_to_receive = conect.recv(1024).decode() # um dicionario  {nome:tamanho} do cliente 
        if size_to_receive == "BREAK": # se ele desistir de enviar apenas passe
            pass 
        else:    #se ele não desistiu de enviar vai chegar ao servidor um dicionario com {nome:tamanho} do arquivo para receber
            separador = size_to_receive.find(":") # encontando o separador 
            arquivo = b""        # byte a ser concatenado 
            while int(size_to_receive[separador+1:]) > len(arquivo): # verificar tamanho do arquivo recebido e maior que o byte concatenado
                read = conect.recv(4096) # escutando
                arquivo += read #concatenando oque foi recebido
            Criar_Arquivo(size_to_receive[:separador],arquivo) # criando um arquivo com nome.extensão recebido acima e o bit concatenado 
            print(f"Recebido {size_to_receive[:separador]} size:{size_to_receive[separador+1:]} from {cliente[0]}") #print para indicar a criação do arquivo 
    if msg == b"&&&":
        break
sock.close()
# fim do programa :)