#!/usr/bin/python3
# coding: utf-8
import socket,threading,json
import enisenet.server as server

class Reception(threading.Thread):
    def __init__(self,manager,socket,lostconn):
        ''' initialisation du thread de réception '''
        threading.Thread.__init__(self)
        self.__manager  = manager  # gestionnaire de connexion
        self.__socket   = socket   # socket à écouter
        self.__lostconn = lostconn # fonction à appeler si perte de connectivité
        self.__actions  = {}       # actions sur réception d'événements

    def __process(self,msg):
        ''' traitement d'un message reçu '''
        try:
            struct = json.loads(msg)
        except Exception as error:
            print('Erreur de décodage du message',msg)
        else:
            event  = struct['event']
            # si des callbacks sont associés à l'événement
            if event in self.__actions:
                sender = struct['sender']
                pseudo = struct['pseudo']
                data   = struct['data']
                if (event==server.SERVERINFO
                    or event==server.SERVERLIST
                    or event==server.SERVERIDENT) and not sender==server.SERVER:
                    return
                # on déclenche les callbacks
                for action in self.__actions[event]:
                    action(self.__manager.player(sender),pseudo,data)
  
    def on(self,event,action):
        ''' mémorise l'action associée à un événement '''
        if event in self.__actions:
            self.__actions[event].append(action)
        else:
            self.__actions[event] = [action]

    def run(self):
        ''' réception et traitement des messages issus du serveur '''
        while True:
            try:
                # attente (bloquante) d'un nouveau message du serveur
                msg    = self.__socket.recv(4096)
                msg    = msg.decode(encoding='utf8')
                # on sépare les messages au cas où
                # on en aurait récupéré plusieurs d'un coup
                lstmsg = msg.split(server.SEP)[0:-1]
                if msg=='':
                    # la connexion est perdue
                    break
                else:
                    # traitement du (ou des ...) message(s)
                    for msg in lstmsg:
                        self.__process(msg)
            except Exception as error:
                print("Connect : error",error.args[1])
                break
        # appel du callback de perte de connexion
        self.__lostconn()
        print("Connect : connection is lost")

class Connect():
    def __init__(self,manager,host,port,pseudo,lostconn=lambda:None):
        ''' ouvre la connexion avec le serveur 
        et crée le thread de réception des messages'''
        self.__socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        try:
            self.__socket.connect((host,port))
        except Exception as error:
            # appel du callback de perte de connexion
            lostconn()
            print("Connect error on connect :",error.args[1])
        else:
            # le client décline son identité (pseudo) auprès du serveur
            self.emit(server.SERVER,server.IDENTITY,pseudo)
            # on crée le thread d'écoute
            self.__reception = Reception(manager,self.__socket,lostconn)
            # on binde quelques événements
            self.__reception.on(server.CONSOLE,
                                lambda s,p,d:print(p,'('+str(s)+') :',d))
            self.__reception.on(server.SERVERINFO,
                                lambda s,p,d:print(d))
            self.__reception.on(server.SERVERLIST,
                                lambda s,p,d:print('Il y a',len(d),'joueur(s) connecté(s)'))
            self.__reception.on(server.SERVERSTART,
                                lambda s,p,d:print("C'est parti !"))
            self.__reception.on(server.SERVERSTOP,
                                lambda s,p,d:print("En attente de joueurs ..."))
            
    def __send(self,struct):
        ''' envoi d'un dictionnaire '''
        msg = bytes(json.dumps(struct)+server.SEP,'utf8')
        try:
            self.__socket.sendall(msg)
        except Exception as error:
            print("Connect error on sending message :",error.args[1])
             
    def listen(self):
        ''' démarre le thread de réception des messages '''
        try:
            self.__reception.setDaemon(1)
            self.__reception.start()
        except Exception as error:
            pass  # chut ...
        
    def on(self,event,action):
        ''' mémorise l'action associée à un événement '''
        try:
            self.__reception.on(event,action)
        except Exception as error:
            pass  # chut ...

    def all(self,event,data):
        ''' diffuse un événement vers tous les clients '''
        struct             = {}
        struct['event']    = event
        struct['dispatch'] = 'all'
        struct['data']     = data
        self.__send(struct)
    
    def broadcast(self,event,data):
        ''' diffuse un événement vers les autres clients '''
        struct             = {}
        struct['event']    = event
        struct['dispatch'] = 'broadcast'
        struct['data']     = data
        self.__send(struct)

    def emit(self,client,event,data):
        ''' émet un événement vers un client particulier '''
        struct             = {}
        struct['event']    = event
        struct['dispatch'] = 'emit'
        struct['to']       = client
        struct['data']     = data
        self.__send(struct)
        
    def close(self):
        ''' ferme le socket de communication avec le serveur '''
        try:
            self.__socket.shutdown(1)
            self.__socket.close()
        except Exception as error:
            pass  # chut ...
 
        
