#!/usr/bin/python3
# coding: utf-8

import enisenet.server as server
from tkinter import *

RED   = 'gainsboro'
GREEN = 'snow'

class ControlPanel(Frame):
    def __init__(self,parent,*args,**kwargs):
        if 'connexion' in kwargs:
            self.connManager = kwargs.pop('connexion')
        if 'chat' in kwargs:
            self.__chat = kwargs.pop('chat')
        else:
            self.__chat = False
        if 'pseudo' in kwargs:
            self.__pseudo = kwargs.pop('pseudo')
        else:
            self.__pseudo = True
        if 'console' in kwargs:
            self.__console = kwargs.pop('console')
        else:
            self.__console = True
        Frame.__init__(self,parent,*args,**kwargs)
        # self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        # Frame1 en haut : serveur et pseudo
        self.Frame1 = Frame(self,borderwidth=2,relief=GROOVE,bg=RED)
        self.Label1 = Label(self.Frame1,text="Serveur",bg=RED)
        self.Label1.grid(row=0,column=0,padx=5,pady=5,sticky=W+E)
        self.HOST = StringVar()
        self.HOST.set('localhost')
        Entry(self.Frame1,textvariable=self.HOST).grid(row=0,column=1,padx=5,pady=5,sticky=W+E)
        if self.__pseudo:
            self.Label2 = Label(self.Frame1,text="Pseudo",bg=RED)
            self.Label2.grid(row=0,column=2,padx=5,pady=5,sticky=W+E)
        self.PSEUDO = StringVar()
        self.PSEUDO.set('yo')
        if self.__pseudo:
            Entry(self.Frame1,textvariable=self.PSEUDO).grid(row=0,column=3,padx=5,pady=5,sticky=W+E)
        self.ButtonConnexion = Button(self.Frame1,text='Connexion',command=self.connection)
        self.ButtonConnexion.grid(row=0,column=4,padx=5,pady=5,sticky=W+E)
        self.Frame1.grid(row=0,column=0,sticky=W+E)
        if self.__console:
            # Frame 2 au milieu : affichage des messages
            self.Frame2        = Frame(self,borderwidth=2,relief=GROOVE,bg=RED)
            #self.ZoneReception = Text(Frame2,width=80,height =4,state=DISABLED)
            self.ZoneReception = Text(self.Frame2,width=20,height=3,state=DISABLED)
            self.ZoneReception.grid(row=0,column=0,padx=5,pady=5,sticky=W+E)
            scroll        = Scrollbar(self.Frame2,command=self.ZoneReception.yview)
            self.ZoneReception.configure(yscrollcommand=scroll.set)
            scroll.grid(row=0,column=1,padx=5,pady=5,sticky=E+S+N)
            self.Frame2.grid(row=1,column=0,pady=5,sticky=W+E)
            self.Frame2.columnconfigure(0,weight=1)
        if self.__chat:
            # Frame 3 en bas : envoi de message au serveur
            Frame3 = Frame(self,borderwidth=2,relief=GROOVE)
            self.MESSAGE  = StringVar()
            self.MsgEntry = Entry(Frame3,textvariable=self.MESSAGE,state=DISABLED)
            self.MsgEntry.grid(row=0,column=0,padx=5,pady=5,sticky=W+E)
            self.ButtonEnvoyer = Button(Frame3,text ='Envoyer',command=self.sendMessage,state=DISABLED)
            self.ButtonEnvoyer.grid(row=0,column=1,padx=5,pady=5)
            self.MsgEntry.bind('<Return>',lambda evt:self.ButtonEnvoyer.invoke())
            self.MsgEntry.bind('<KP_Enter>',lambda evt:self.ButtonEnvoyer.invoke())
            Frame3.grid(row=2,column=0,padx=5,pady=5,sticky=W+E)
            Frame3.columnconfigure(0,weight=1)
        # on place des callbacks sur les événements réseau
        if hasattr(self,'connManager'):
            self.connManager.on(server.CONSOLE,
                                lambda s,p,d:self.displayMessage(p+' ('+str(s)+') : '+d))
            self.connManager.on(server.SERVERINFO,
                                lambda s,p,d:self.displayMessage(d))
            self.connManager.on(server.SERVERLIST,
                                lambda s,p,d:self.displayMessage('Il y a '+str(len(d))+' joueur(s) connecté(s)'))
            self.connManager.on(server.SERVERSTART,
                                lambda s,p,d:self.started("C'est parti !"))
            self.connManager.on(server.SERVERSTOP,
                                lambda s,p,d:self.stopped("En attente de joueurs ..."))
        else:
            print("ControlPanel : no connexion manager !")


    def started(self,msg):
        if self.__console:
            self.Frame2.configure(bg=GREEN)
            self.displayMessage(msg)

    def stopped(self,msg):
        if self.__console:
            self.Frame2.configure(bg=RED)
            self.displayMessage(msg)
    
    def connection(self):
        ''' bouton de connexion '''
        if hasattr(self,'connManager'):
            # on met à jour l'interface
            self.connected()
            # on lance la connexion
            host   = self.HOST.get()
            pseudo = self.PSEUDO.get()
            self.connManager.hello(host,pseudo,self.disconnected)
        else:
            print("ControlPanel : no connexion manager !")

    def disconnection(self):
        ''' bouton de déconnexion '''
        if hasattr(self,'connManager'):
            # on met à jour l'interface
            self.disconnected()
            # on ferme la connexion
            self.connManager.goodbye()
        else:
            print("ControlPanel : no connexion manager !")
 
    def sendMessage(self):
        ''' bouton d'envoi de message '''
        # on lit le message dans le champ de saisie
        msg = self.MESSAGE.get()
        # si le message n'est pas vide
        if not msg=='':
            # on envoie le message à tout le monde
            self.connManager.all(server.CONSOLE,msg)
             # on efface le champ de saisie
            self.MESSAGE.set('')
                     
    def connected(self):
        ''' handler de connexion '''
        self.Frame1.configure(bg=GREEN)
        self.Label1.configure(bg=GREEN)
        if self.__pseudo:
            self.Label2.configure(bg=GREEN)
        self.ButtonConnexion.configure(text='Déconnexion',command=self.disconnection)
        if self.__chat:
            self.MsgEntry.configure(state=NORMAL)
            self.ButtonEnvoyer.configure(state=NORMAL)
    
    def disconnected(self):
        ''' handler de déconnexion '''
        self.Frame1.configure(bg=RED)
        self.Label1.configure(bg=RED)
        if self.__pseudo:
            self.Label2.configure(bg=RED)
        if self.__console:
            self.Frame2.configure(bg=RED)
        self.ButtonConnexion.configure(text='Connexion',command=self.connection)
        if self.__chat:
            self.MsgEntry.configure(state=DISABLED)
            self.ButtonEnvoyer.configure(state=DISABLED)

    def displayMessage(self,msg):
        if self.__console:
            ''' affichage d'un message réseau '''
            if not self.ZoneReception.get(1.0, "end-1c")=='':
                msg = '\n'+msg
            self.ZoneReception.config(state=NORMAL)
            self.ZoneReception.insert(END,msg)
            self.ZoneReception.yview(END)
            self.ZoneReception.config(state=DISABLED)
