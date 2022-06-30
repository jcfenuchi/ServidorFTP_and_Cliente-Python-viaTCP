#!/usr/bin/env python
# -*- coding: utf-8 -*-

#bibliotecas ultilizada ---
import os     
import socket
import time




#Padrão Cleinte TCP                                             #
SERVER = '127.0.0.1'                                            #
PORT   = 12345                                                  #
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        #
sock.connect((SERVER,PORT))                                     #

Client_Dowload_And_Upload = "ClientFTP_TCP_Files_DowloadAnd_Upload" # nome do Diretorio de onde o cliente 
                                                        #vai receber Dowload/Upload  no servidor

def encontrar_pasta(caminho):                                     # Função para encontrar o caminho da pasta colocada acima
    caminho_atual = os.getcwd()    # pega o caminho onde o VS_está executando
    for raiz, diretorios, arquivos in os.walk(caminho_atual):        # for para andar nos dir a partir no caminho_atual
        for diretorio in diretorios:                             #for para caminhar em todos os diretorios
            if caminho in diretorio:           # se a pasta "ClientFTP_TCP_Files_DowloadAnd_Upload" estiver in diretorio ou seja
                return raiz+"/"+diretorio     #se ele encontrar um Diretorio com o nome acima retorna o Path a partir do / ate a pasta

def Ler_arquivo(nome_arquivo):   # ler conteudo do arquivo , função para Upload de arquivo no servidor!
    caminho = encontrar_pasta(Client_Dowload_And_Upload)+"/"+nome_arquivo # caminho função encontrar caminho +/nome_do_arquivo
    try:                # tentar  abrir arquivo 
        with open(caminho, "rb") as arquivo: # abrir o arquivo em Bytes
            read = arquivo.readlines() # ler todas as linhas
        read = b"".join(read) #bytes Join pois o readlines retorna uma Lista de Bytes
        return read # retorno dos Bytes concatenados
    except PermissionError as e:     #exept para erro
        print("erro de permisão",e)                     #
    except FileNotFoundError as e:                      #         
        print("Arquivo não encontrado!")                #
    except Exception as e:                              #
        print("Erro desconhecido", e)                   #
      

def Criar_Arquivo(nome_arquivo,conteudo):    # função para Criar arquivos após realizar Dowload do servidor 
    try:  # tentar 
        caminho = encontrar_pasta(Client_Dowload_And_Upload)+"/"+nome_arquivo # ver se a pasta Existe dentro do diretorio
        fd = open(caminho, "wb")     # escrever Bytes e criar um arquivo com a sua extensão correta
        fd.write(conteudo)      # escrever conteudo
        fd.close()      # fecha arquivo
    except: # erro para caso a pasta não seja encontrada ele deve criar está pasta 
        atual = os.getcwd()  # pegando o caminho atual ele é executado.
        novo_caminho = atual+"/Cliente_TCP_Dowload_Updload/"+Client_Dowload_And_Upload   #caminho para fazer a pasta
        os.makedirs(novo_caminho) # Criando Diretorios com OS MKDIR / makedirs para uma arvore de diretorios
        fd = open(encontrar_pasta(Client_Dowload_And_Upload)+"/"+nome_arquivo, "wb")   # agora o programa localiza o diretorio acima
        fd.write(conteudo)  # escreve seu conteudo
        fd.close()     # fecha o arquivo criado

def Get_Arquive_And_Legth_Json():   # função para pegar o nome:tamanho do arquivo 
    while True:
        try:
            arquivos_Locais = os.listdir(encontrar_pasta(Client_Dowload_And_Upload)) # caminho onde vai Listar os Arquivos
            arquivos_Json = {} #lista vazia para json
            if arquivos_Locais != None: # verificar se a lista está vazia 
                for arquivo in arquivos_Locais:  # for na lista de arquivos gerada por Listdir
                    tamanho = os.path.getsize(encontrar_pasta(Client_Dowload_And_Upload)+"/"+arquivo) # pegando tamanho
                    arquivos_Json[arquivo]=tamanho # adicionando ao arquivos.Json dicionario arquivo:tamanho
                return arquivos_Json #retornando Dicionarios "Json" para enviar ao cliente as possibilidades de dowload
        except PermissionError as e:                                 # Exepts
            print("erro de permisão",e)
            break       
        except FileNotFoundError as e:                                           # Caso não ache a pasta de Clients Criar ela!
            atual = os.getcwd()                                                                         
            os.mkdir(atual+"Q4/Cliente_TCP_Dowload_Updload/"+Client_Dowload_And_Upload)
            print("Uma pasta foi criada por favor verifique!")
        except Exception as e:         # exept para identificar erros diferentes
            print("Erro desconhecido", e)
            break

def Menu():#Menu de Opções    # Menu principal para seleção de Opções
    opcao = input("""
[1] = Lista arquivos:
[2] = Baixar arquivo:
[3] = enviar arquivo:
[4] = Sair
Resposta:""")
    return opcao

def Mostrar_ListaArquivos(lista_arquivos):  #receber a string "Json"
    lista_arquivos = (lista_arquivos[1:-1].decode()).replace("\'","") #remover aspas e decodifica pega posição sem os {} do inicio e fim
    lista_arquivos = lista_arquivos.split(", ") #separar em uma lista
    for arquivos in lista_arquivos:   # para cada arquivo Nome:NNN onde NNN é o tamanho
        separador = arquivos.find(":")  # encontre :
        print(f"Nome:{arquivos[:separador]:.<30} |tamanho:{arquivos[separador+1:]:.>10} bytes")
        #oque estiver antes dos : é o nome oque estiver depois da posição :+1 é o tamanho :)

def Menuespera():  # menu para não pular um outro menu instataneamente para dar tempo de analisar.
    input("Digite algo ou aperta enter para prosseguir")

def MenuUpload():     # Menu para Updload de arquivos 
    escolha = input("""
|---------- Enviar Arquivos ---------------------------|
|[1]- Listar arquivos to Upload........................| 
|[2]- Voltar ao inicio.................................|
|Digite o Nome Do Arquivo ou uma das Opções Abaixo!....|
|~ /ClientARQUIVO_UPLOAD$:""")
    return escolha

def MenuDowload(): # menu para realização de Dowload
    escolha = input("""
|------- Dowload de Arquivos ----------|
|[2]- para sair........................|
|Digite o nome do arquivo Abaixo.......|
~ /ClientARQUIVO_Dowload$:""")
    return escolha



# PROGRAMA PRINCIPAL PARA FUNCIONAR TUDO 
while True:
    op = Menu()  # menu com as opções que pode ser escolhida pelo client
    if op == "1":    # se a opção for 1 entre aqui
        msg = sock.send("LS&".encode())  # enviar um bit"caractere" ao servidor indicando a opção & para listar.
        if msg: # se for enviada 
            quantidade = int(sock.recv(512).decode()) # o servidor vai enviar a quantidade de arquivos que vai mandar.
            time.sleep(0.3) # 0.3 segundos de espera.
            if quantidade: # se recebido com sucesso começar a capturar a lista de arquivos
                menu_escolha = b""  # Bit vazio
                while quantidade > len(menu_escolha): # ficar recebendo Bits enquando o tamanho da variavel for inferior    
                    read = sock.recv(1024)                  # a o tamanho do arquivo
                    menu_escolha += read     #ler ate completar
            print("------ ARQUIVOS DO SERVIDOR PARA DOWLOAD ------") # telinha de perfumaria             
            Mostrar_ListaArquivos(menu_escolha)  #Menu para Exibição bonita.
            Menuespera()        # Menu para não pular novamente as opções
    if op == "2": # opção do menu principal for 2 entre aqui 
        msg = sock.send("CP&".encode()) #envia comando CP& ao servidor
        valido = False  # analise se o arquivo é valido para dowload
        while valido == False: # repita enquando o arquivo não for valido 
            ArquivoDowload = MenuDowload() #pergunta o nome do arquivo para Dowload
            if ArquivoDowload == "2": # se a reposta for 2 significa que o client deseja sair
                sock.send(b"BREAK")  # enviado codigo de saida do loop para o socket
                break  # break
            sock.send(ArquivoDowload.encode()) # envio do nome ao servidor
            time.sleep(0.2) # time para não sobrecaregar socket
            serve_response = sock.recv(512) # Reposta do server 200=OK,404=não encontrado Tente novamente
            if serve_response[0:3] == b"200": # se as primeira 3 msg for 200 deu certo
                print("Solicitado com Sucesso! ...")  # print de sucesso
                size_arquivo = int(sock.recv(1024).decode()) # recebendo tamanho total do arquivo do servidor
                arquive_receive = b"" # Bit vazio para receber arquivo
                while size_arquivo > len(arquive_receive): #comparação de tamanhos 
                        read = sock.recv(4096)  # receber enquanto o tamanho recebido for menor do que o tam total recebido do serv
                        arquive_receive += read  # concatenação de bits 
                Criar_Arquivo(ArquivoDowload,arquive_receive) # usando a função para criar arquivos
                print(f"$ {ArquivoDowload} foi Arquivo criado Na pasta de Dowloads/Upload") # print para aviso
                valido = True # saindo do LOOP
            if serve_response == b"404": # sinalização de erro pelo servidor
                print(f"Arquivo {ArquivoDowload}, Não foi encontrado tente novamente!")#nome de arquivo não liberado pelo servidor
    if op == "3":  # se a msg no menu for 3 entre aqui 
        msg = sock.send("POST&".encode()) # envia comando ao servidor 
        if msg: # se enviada 
            arquivo_valido = False # variavel de suporte para analise de arquivo
            while arquivo_valido == False:  # enquanto a variavel de suporte for false repita
                arquivo_name_to_upload = MenuUpload()  # atribuindo menu de Upload a uma variavel
                arquivos_to_send = Get_Arquive_And_Legth_Json() # pegando "json" arquivos dentro da pasta de Upload/dowload do CLient 
                if arquivo_name_to_upload == "1": #o MenuUpload for digitado 1 significa que o usuario quer ver a lista de arquivos
                    lista_arquivo = Get_Arquive_And_Legth_Json() #pegando lista de arquivos do dir (client upload e dowload)
                    lista_arquivostr = str(lista_arquivo)  # transformando dicionario em string ( movtivo abaixo )
                    lista_arquivobyte = lista_arquivostr.encode()#transformando em bytes para funcionar na função mostrar arquivos
                    print("------ MENU DE ARQUIVOS PARA UPLOAD ------")   # menu de perfumaria
                    Mostrar_ListaArquivos(lista_arquivobyte)# mostrar Lista de arquivos recebe Bytes igual a OP = 1 
                    pass
                elif arquivo_name_to_upload in arquivos_to_send.keys(): # se o nome do arquivo estiver uma chave siginifica que ele é apto para ser enviado
                    size_to_upload = arquivos_to_send[arquivo_name_to_upload]#pegando tamanho do arquivo
                    size_send_to_server = sock.send(f"{arquivo_name_to_upload}:{size_to_upload}".encode())#pegando nome e tamanho e enviado ao servidor.
                    if size_send_to_server: # se foi enviado ao servidor 
                        sock.send(Ler_arquivo(arquivo_name_to_upload)) # vai pegar todos os Bytes e enviar ao servidor
                        arquivo_valido = True # mudar estado para valido indicando que o arquivo foi localizado e enviado
                        print(f"{arquivo_name_to_upload} Enviado ao servidor! por favor aguarde!") # confirmação de envio ao usuario
                        time.sleep(0.5) # timer para dar tempo do servidor receber e criar o arquivo
                elif arquivo_name_to_upload == "2": # no menur for digitado 2 significa voltar ao inicio
                    sock.send("BREAK".encode()) # enviando Break ao servidor para deixar de escutar 
                    break # saindo do LOOP
                else: # caso não seja nenhuma opção acima Significa que o arquivo não foi encontrado
                    print(f"Arquivo {arquivo_name_to_upload} Não encontrado! Tente Novamente")#msg ao usuario e reinicio do loop      
    if op == "4": # se op for 4 significa saida do programa 
        sock.send("&&&".encode()) # envio de caracteres para fechar conexão 
        break   # saida do loop de menu 

sock.close()