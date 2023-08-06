from requests import Session
import requests
from signalr import Connection
import json
import uuid
from threading import Thread
import asyncio
class OneiroiConnection:
    clientName=""
    daemonURL=""
    connection=None
    hub=None
    session=requests.Session()   
    responseTimeout=1
    messageHandler=None
    messageHanlers={}
    AllNodeStructureList=None
    #set session parameters 
    session.params={ 'clientID':clientName}   
    def __init__(self,clientid,oneiroi_daemonURL):  
        self.clientName=clientid
        self.daemonURL=oneiroi_daemonURL       
        #create a connection
        self.connection = Connection(self.daemonURL,self.session)
        #register hub proxy and methods
        self.hub = self.connection.register_hub('OneiroiBecosHub')
    def connect_to_Daemon(self):                   
            def ServerResponse(arg1=None, arg2=None):
                if arg2:
                    handler=self.get_Message_Handler(arg1)
                    if handler:
                        handler.OnNodeResponse(arg1,arg2)                
            def UpdateAttributeValue(NodeName,AttributeName,SourceClient,AttributeValue):
                 handler=self.get_Message_Handler(NodeName)
                 if handler:
                     handler.OnAttributeValueReceived(SourceClient,NodeName,AttributeName,AttributeValue)
            def OnMessageDeliveryAck(acknowledgement):
                print("parse OBJ")
            def OnMessageReceived(MessageID,NodeName,Message):
                 handler=self.get_Message_Handler(NodeName)
                 if handler:
                     handler.OnMessageReceived(MessageID,NodeName,Message['xmlData'])  
            def AllNodeStructureReceived(NodeStructrueList):
                 self.AllNodeStructureList=NodeStructrueList
            #initiate connection request
            self.hub.client.on('Response',ServerResponse)   
            self.hub.client.on('updateAttributevalue',UpdateAttributeValue) 
            self.hub.client.on('messageDeliveryAck',OnMessageDeliveryAck)   
            self.hub.client.on('UpDateClient',OnMessageReceived)
            self.hub.client.on('onAllNodeStructure',AllNodeStructureReceived)
            self.connection.start()           
            self.hub.server.invoke('getAllnodesWithStructure')        
            self.connection.wait(2)
    def connect_To_Node(self,NodeName,MessageHandler):
        self.messageHanlers[NodeName]=MessageHandler
        self.hub.server.invoke('CreateNode', NodeName)
        self.connection.wait(self.responseTimeout)
    def Subscribe_To_Node_Messages(self,NodeName):
        self.hub.server.invoke('subScribe',self.clientName,  NodeName)
        self.connection.wait(self.responseTimeout)
    def unsubscribe_From_Node_Message(self,NodeName):
        self.hub.server.invoke('UNsubScribe',self.clientName,NodeName)
        self.connection.wait(self.responseTimeout)
    def Set_Attribute_Value(self,NodeName,AttributeName,AttributeValue):
        self.hub.server.invoke('setAttributeValue',NodeName,AttributeName ,AttributeValue,self.clientName)
        self.connection.wait(self.responseTimeout)
    def get_Attribute_value(self,NodeName,AttributeName):
        self.hub.server.invoke('getAttributeValue',NodeName,AttributeName ,self.clientName)
        self.connection.wait(self.responseTimeout)
    def get_Attribute_value_ofClient(self,NodeName,AttributeName,ClientID):
        self.hub.server.invoke('getAttributeValue',NodeName,AttributeName ,ClientID)
        self.connection.wait(self.responseTimeout)
    def Set_Node_Attribute_Notification(self,NodeName,AttributeName,):
        self.hub.server.invoke('setNotificationForAttribute',self.clientName,NodeName,AttributeName)
        self.connection.wait(self.responseTimeout)
    def Send_Message(self,xmlMessage):
        print( str(uuid.uuid4()))
        self.hub.server.invoke('handleOneiroiMessage', str(uuid.uuid4()) ,xmlMessage)
        self.connection.wait(self.responseTimeout)    
    def keep_listening(self,duration_in_Seconds=3600):       
        self.hub.server.invoke('inform', self.clientName)        
        self.connection.wait(duration_in_Seconds)
    def get_Message_Handler(self,NodeName):
        if len(self.messageHanlers)>0:
            return self.messageHanlers[NodeName]
        else:
            return None
    def get_Node_Structure(self,NodeName):
        currentNodeDefinition=None
        if self.AllNodeStructureList:
            for node in self.AllNodeStructureList:
                if node['NodeName']==NodeName:
                    currentNodeDefinition=node
                    break
        return currentNodeDefinition
        
        