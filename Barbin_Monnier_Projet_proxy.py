import socket, sys
from _thread import start_new_thread

taille_buffer = 4096
port_ecoute = 7000
max_de_connexion = 5


def requete_http(server_web, port, connexion, client, addresse):
    
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server_socket.connect((server_web, port))
        server_socket.send(client.encode('utf-8'))

        while True:
            reponse = server_socket.recv(taille_buffer)
            
            if (len(reponse) > 0):
                connexion.send(reponse)
                print(f'[*] Requete effectuee ! {addresse[0]}')
                print('Reponse : ', reponse)
                
            else:
                connexion.send(reponse)
                break
            
        server_socket.close()
        connexion.close()
        
    except socket.error:
        server_socket.close()
        connexion.close()
        sys.exit(1)


def requete_https(server_web, port, connexion, client, addresse):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Si fonctionne : envoie le code 200 (status OK)
        s.connect((server_web, port))
        reply = "HTTP/1.0 200 Connexion etablie\r\n"
        reply += "Proxy-agent: SigmaIDU\r\n"
        reply += "\r\n"
        connexion.sendall(reply.encode())
        
    except socket.error as err:
        pass
    
    connexion.setblocking(0)
    s.setblocking(0)
    
    while True:
        
        try:
            request = connexion.recv(taille_buffer)
            s.sendall(request)
            
        except socket.error as err:
            pass

        try:
            reply = s.recv(taille_buffer)
            connexion.sendall(reply)
            
        except socket.error as e:
            pass
  

def connect_string(connexion, client: bytes, addresse):
    
    client = client.decode("latin-1")
    
    try:
        first_line = client.split('\n')[0]
        print(f'\n\nPremiere ligne : {first_line}')
        url = first_line.split(' ')[1]
        http_pos = url.find("://")  # Recherche de la position de ://
        
        if (http_pos == -1):
            temp = url
            
        else:
            temp = url[(http_pos + 3):]  # prend le reste de l'url
        port_pos = temp.find(":")  # recupère l'index du port
        webserver_pos = temp.find("/")  # obtenient l'index de la fin du serveur web

        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1
        
        if (port_pos == -1 or webserver_pos < port_pos):
            port = 80
            webserver = temp[:webserver_pos]
            
        else:
            port = int((temp[port_pos + 1:])[:webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]
        print(f'Webserver : {webserver} \nPort : {port}')
        server_proxy(webserver, port, connexion, client, addresse)
        
    except Exception as e:
        print("ERRR", e)
        sys.exit(1)


def server_proxy(server_web, port, connexion, client, addresse):
    
    method = client.split(" ")[0]
    
    try:
        
        if (method == "CONNECT"):
            requete_https(server_web, port, connexion, client, addresse)
            
        else:
            # on crée une nouvelle socket qui va envoyer la requete pour le client
            requete_http(server_web, port, connexion, client, addresse)
            
    except Exception as e:
        print("Erreur de traitement de la demande par le serveur ", e)
        sys.exit(1)


def run():
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # initialise socket
        print("[*] Initialisation des sockets")
        client_socket.bind(('localhost', port_ecoute))
        print("[*] Socket liés avec succès")
        client_socket.listen(max_de_connexion)
        print(f"[*] Server commence a ecouter sur : {port_ecoute}")
        
    except Exception as e:
        print(f"[*] Erreur {e} \n[*] Impossible d'initialiser la socket")
        sys.exit(2)

    while True:
        
        try:
            connexion, addresse = client_socket.accept()
            client = connexion.recv(taille_buffer)
            start_new_thread(connect_string, (connexion, client, addresse))
            
        except KeyboardInterrupt:
            client_socket.close()
            print(f"[*] KeyboardInterrupt :-> Proxy server Shutting Down")
            sys.exit()

run()