#!/usr/bin/python3
# coding: utf-8
import socket,threading,json

# les clients actifs
sockets = {}
groups  = []

# verrouillage de l'accès aux ressources partagées
# (variables globales et sockets)
# pour les threads gestionnaires de client
LOCK    = threading.Lock()

# constantes
SERVER       = 'Info'
CONSOLE      = 'console'
SERVERPSEUDO = 'Server'
SERVERINFO   = 'serverinfo'
SERVERLIST   = 'clientslist'
SERVERIDENT  = 'serverident'
SERVERSTART  = 'serverstart'
SERVERSTOP   = 'serverstop'
SERVERNOB    = False
IDENTITY     = 'identity'
SEP          = '\u001F'

def message(*args):
    if VERBOSE:
        print(*args)

class ClientManager(threading.Thread):
    def __init__(self,conn):
        '''initialisation de la communication avec un client'''
        threading.Thread.__init__(self)
        # mémorisation du socket
        self.socket = conn
        # mémorisation du port de connexion
        self.port   = str(self.socket.getpeername()[1])
        self.pseudo = SERVERNOB
        with LOCK:
            # mémorisation du nouveau client
            sockets[self.port] = self.socket
            # placement du nouveau client dans un groupe
            done = False
            for group in groups:
                if len(group)<PLAYERS:
                    player = [self.port, self.pseudo, len(group)]
                    group.append(player)
                    done = True
                    break
            if not done:
                player = [self.port, self.pseudo, 0]
                groups.append([player])
            # message de confirmation de connexion
            message("Server : got contact from",self.socket.getpeername())
            struct             = {}
            struct['sender']   = SERVER
            struct['pseudo']   = SERVERPSEUDO
            struct['event']    = SERVERINFO
            struct['data']     = "Connecté sur le port "+self.port
            self.emit(self.port,struct)
    
    def __group(self):
        for group in groups:
            for player in group:
                if player[0] == self.port:
                    return group
        return []

    def __process(self,msg):
        ''' traitement d'un message reçu '''
        message("Server : got client message from "+self.port+", ",msg)
        try:
            struct = json.loads(msg)
        except Exception as error:
            message('Erreur de décodage du message',msg)
        else:
            with LOCK:
                dispatch = struct['dispatch']
                # si le message est un ordre au serveur
                if dispatch=='emit' and struct['to']==SERVER:
                    event = struct['event']
                    if event==IDENTITY:
                        # mise à jour du pseudo
                        self.pseudo = struct['data']
                        # mise à jour dans le groupe
                        for player in self.__group():
                            if player[0] == self.port:
                                player[1] = self.pseudo
                        message("Server : got pseudo",self.pseudo,"from",self.port)
                        # envoi du numéro de port au client qui vient de s'identifier
                        struct             = {}
                        struct['sender']   = SERVER
                        struct['pseudo']   = SERVERPSEUDO
                        struct['event']    = SERVERIDENT
                        struct['data']     = self.port
                        self.emit(self.port,struct)
                        # envoi d'un message d'info
                        struct             = {}
                        struct['sender']   = SERVER
                        struct['pseudo']   = SERVERPSEUDO
                        struct['event']    = SERVERINFO
                        struct['data']     = "Le joueur "+self.pseudo+" ("+self.port+") "+" vient de se connecter"
                        self.broadcast(self.__group(),struct)
                        # envoi de la nouvelle liste des connectés
                        struct             = {}
                        struct['sender']   = SERVER
                        struct['pseudo']   = SERVERPSEUDO
                        struct['event']    = SERVERLIST
                        struct['data']     = self.__group()
                        self.all(self.__group(),struct)
                        message("Server : group ",self.__group())
                        # si le nombre de joueurs nécessaires est atteint
                        if len(self.__group())==PLAYERS:
                            # envoi du message de partie active
                            struct             = {}
                            struct['sender']   = SERVER
                            struct['pseudo']   = SERVERPSEUDO
                            struct['event']    = SERVERSTART
                            struct['data']     = None
                            self.all(self.__group(),struct)
                        else:
                            # envoi du message de partie inactive
                            struct             = {}
                            struct['sender']   = SERVER
                            struct['pseudo']   = SERVERPSEUDO
                            struct['event']    = SERVERSTOP
                            struct['data']     = None
                            self.all(self.__group(),struct)
                            
                # si le message doit être retransmis
                else:
                    # si le groupe est complet on transmet
                    # sinon le message est bloqué
                    if len(self.__group()) == PLAYERS:
                        struct['sender'] = self.port
                        struct['pseudo'] = self.pseudo
                        if dispatch=='all':
                            self.all(self.__group(),struct)
                        elif dispatch=='broadcast':
                            self.broadcast(self.__group(),struct)
                        elif dispatch=='emit':
                            self.emit(struct['to'],struct)
                        else:
                            message("Unknown dispatch type :",dispatch)

    def __end(self):
        ''' opérations de fermeture '''
        with LOCK:
            # suppression du joueur de son groupe
            mygroup = self.__group()
            for i in range(len(mygroup)):
                if mygroup[i][0] == self.port:
                    pos = i
                    break
            mygroup.pop(pos)
            # renumerotation des joueurs restants
            for i in range(len(mygroup)):
                mygroup[i][2]=i
            # message de confirmation de déconnexion
            struct             = {}
            struct['sender']   = SERVER
            struct['pseudo']   = SERVERPSEUDO
            struct['event']    = SERVERINFO
            struct['data']     = "Vous êtes déconnecté"
            self.emit(self.port,struct)
            message("Server : client",self.pseudo+" ("+self.port+")","disconnected")
            # message d'information à tous les autres clients
            struct             = {}
            struct['sender']   = SERVER
            struct['pseudo']   = SERVERPSEUDO
            struct['event']    = SERVERINFO
            struct['data']     = "Le joueur "+self.pseudo+" ("+self.port+") "+" vient de se déconnecter"
            self.broadcast(mygroup,struct)
            
            # suppression du socket de la liste des sockets actifs
            del sockets[self.port]
            # brassage des groupes incomplets
            self.__optimizeGroups()
        # fermeture du socket
        try:
            self.socket.shutdown(1)
            self.socket.close()
        except Exception as error:
            pass  # chut ...

    def __optimizeGroups(self):
        global groups
        orphans   = []
        newgroups = []
        # on fait la liste des joueurs qui ne sont pas
        # dans un groupe complet (-> orphans)
        for group in groups:
            if len(group)==0:
                pass
            elif len(group)<PLAYERS:
                for player in group:
                    orphans.append(player)
            else:
                newgroups.append(group)
        # on replace tous les joueurs de la liste
        # dans des nouveaux groupes
        for i in range(0,len(orphans),PLAYERS):
            # nouveau groupe
            group = orphans[i:i+PLAYERS]
            # renumerotation des joueurs
            for i in range(len(group)):
                group[i][2]=i
            # envoi de la nouvelle liste des connectés
            struct             = {}
            struct['sender']   = SERVER
            struct['pseudo']   = SERVERPSEUDO
            struct['event']    = SERVERLIST
            struct['data']     = group
            self.all(group,struct)
            # si le pool est complet ça joue
            if len(group)==PLAYERS:
                # envoi du message de partie active
                struct             = {}
                struct['sender']   = SERVER
                struct['pseudo']   = SERVERPSEUDO
                struct['event']    = SERVERSTART
                struct['data']     = None
                self.all(group,struct)
            else:
                # envoi du message de partie inactive
                struct             = {}
                struct['sender']   = SERVER
                struct['pseudo']   = SERVERPSEUDO
                struct['event']    = SERVERSTOP
                struct['data']     = None
                self.all(group,struct)
            # on mémorise le nouveau groupe
            newgroups.append(group)
        # on met à jour les groupes  
        groups = newgroups            
    
    def __send(self,socket,struct):
        ''' envoi d'un dictionnaire '''
        msg = bytes(json.dumps(struct)+SEP,'utf8')
        try:
            socket.sendall(msg)
        except Exception as error:
            message("Server error on send :",error.args[1])

    def run(self):
        ''' réception et traitement des messages issus du client '''
        while True:
            try:
                # attente d'un nouveau message du client (bloquante)
                msg = self.socket.recv(4096)
                msg = msg.decode(encoding='utf8')
                # on sépare les messages au cas où
                # on en aurait récupéré plusieurs d'un coup
                lstmsg = msg.split(SEP)[0:-1]
                if msg == '':
                    # la connexion est perdue
                    break
                else:
                    # traitement du (ou des ...) message(s)
                    for msg in lstmsg:
                        self.__process(msg)
            except Exception as error:
                message("Server error on broadcast :",error.args[1])
                break
        # opérations de fermeture
        self.__end()
            
    def all(self,group,struct):
        '''  diffuse un événement vers tous les clients '''
        for player in group:
            self.__send(sockets[player[0]],struct)
            
    def broadcast(self,group,struct):
        '''  diffuse un événement vers les autres clients '''
        for player in group:
            if not player[0] == self.port:
                self.__send(sockets[player[0]],struct)

    def emit(self,port,struct):
        '''  diffuse un événement vers un client particulier '''
        self.__send(sockets[port],struct)

class ListenToClients(threading.Thread):
    def __init__(self,socket):
        ''' initialisation du thread d'écoute '''
        threading.Thread.__init__(self)
        self.__socket = socket
        try:
            self.__socket.listen(5)
        except Exception as error:
            message("Server warning on listen :",error.args[1])
        else:
            message("Server is up on port",self.__socket.getsockname()[1])
       
    def run(self):
        ''' boucle de traitement des demandes de connexion '''
        while True:
            try:
                # attente (bloquante) d'une nouvelle demande de connexion
                socket,adresse = self.__socket.accept()
            except Exception as error:
                message("Server error on accept :",error.args[1])
                break
            else:
                # on crée un thread pour gérer la connexion
                client = ClientManager(socket)
                client.setDaemon(1)
                client.start()

class Server():
    def __init__(self,port,nbPlayers,verbose=False):
        ''' création du socket d'écoute et du thread d'écoute '''
        global PLAYERS,VERBOSE
        PLAYERS = nbPlayers
        VERBOSE = verbose
        self.__clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clientsocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        try:
            self.__clientsocket.bind(('', port))
        except Exception as error:
            message("Server error on bind :",error.args[1])
        else:
            clientsListener = ListenToClients(self.__clientsocket)
            clientsListener.setDaemon(1)
            clientsListener.start()

