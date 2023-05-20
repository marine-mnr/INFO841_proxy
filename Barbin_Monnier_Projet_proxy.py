import socket, sys
from _thread import start_new_thread

taille_buffer = 4096
port_ecoute = 7000
max_de_connexion = 5


def requete_http(server_web, port, connexion, client, addresse):
    # Fonction pour traiter les requêtes HTTP
    
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Se connecte au serveur web
        server_socket.connect((server_web, port))
        # Envoie la requête du client au serveur web
        server_socket.send(client.encode('utf-8'))

        while True:
            # Reçoit la réponse du serveur web
            reponse = server_socket.recv(taille_buffer)
            
            if len(reponse) > 0:
                # Envoie la réponse au client
                connexion.send(reponse)
                print(f'[*] Requete effectuee ! {addresse[0]}')
                print('Reponse : ', reponse)
                
            else:
                # Si la réponse est vide, arrête la boucle
                connexion.send(reponse)
                break
            
        server_socket.close()
        connexion.close()
        
    except socket.error:
        server_socket.close()
        connexion.close()
        sys.exit(1)


def requete_https(server_web, port, connexion, client, addresse):
    # Fonction pour traiter les requêtes HTTPS
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Si cela fonctionne : envoie le code 200 (status OK) au client
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
            # Reçoit la requête du client
            request = connexion.recv(taille_buffer)
            # Envoie la requête au serveur web
            s.sendall(request)
            
        except socket.error as err:
            pass

        try:
            # Reçoit la réponse du serveur web
            reply = s.recv(taille_buffer)
            # Envoie la réponse au client
            connexion.sendall(reply)
            
        except socket.error as e:
            pass
  

def connect_string(connexion, client: bytes, addresse):
    # Fonction pour extraire l'URL et le port de la requête du client
    
    client = client.decode("latin-1")
    
    try:
        first_line = client.split('\n')[0]
        print(f'\n\nPremiere ligne : {first_line}')
        url = first_line.split(' ')[1]
        http_pos = url.find("://")  # Recherche de la position de ://
        
        if http_pos == -1:
            temp = url
            
        else:
            temp = url[(http_pos + 3):]  # prend le reste de l'URL
        port_pos = temp.find(":")  # récupère l'index du port
        webserver_pos = temp.find("/")  # obtient l'index de la fin du serveur web

        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1
        
        if port_pos == -1 or webserver_pos < port_pos:
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
    # Fonction pour déterminer la méthode de la requête et appeler la fonction appropriée
    
    method = client.split(" ")[0]
    
    try:
        if method == "CONNECT":
            # Si la méthode est CONNECT, appelle la fonction pour les requêtes HTTPS
            requete_https(server_web, port, connexion, client, addresse)
            
        else:
            # Sinon, appelle la fonction pour les requêtes HTTP
            requete_http(server_web, port, connexion, client, addresse)
            
    except Exception as e:
        print("Erreur de traitement de la demande par le serveur ", e)
        sys.exit(1)


def run():
    # Fonction principale pour exécuter le serveur proxy
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Initialise le socket
        print("[*] Initialisation des sockets")
        client_socket.bind(('localhost', port_ecoute))
        print("[*] Socket lies avec succes")
        client_socket.listen(max_de_connexion)
        print(f"[*] Server commence a ecouter sur : {port_ecoute}")
        
    except Exception as e:
        print(f"[*] Erreur {e} \n[*] Impossible d'initialiser la socket")
        sys.exit(2)

    while True:
        try:
            # Accepte une nouvelle connexion
            connexion, addresse = client_socket.accept()
            # Reçoit la requête du client
            client = connexion.recv(taille_buffer)
            # Démarre un nouveau thread pour traiter la requête
            start_new_thread(connect_string, (connexion, client, addresse))
            
        except KeyboardInterrupt:
            client_socket.close()
            print(f"[*] KeyboardInterrupt :-> Proxy server Shutting Down")
            sys.exit()

run()
