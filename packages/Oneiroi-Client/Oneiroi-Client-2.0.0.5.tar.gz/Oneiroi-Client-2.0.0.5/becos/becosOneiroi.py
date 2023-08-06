from _thread import start_new_thread
from threading import Thread
import threading
import asyncio
import time
from abc import ABC,abstractmethod
import datetime
from time import gmtime, strftime
from requests import Session
import requests
from signalr import Connection
import json
import uuid
from threading import Thread
import asyncio
class OneiroiHandler:
    daemonURL=None
    clientName=None
    NodeConnections={}
    messageText = """<?xml version="1.0" encoding="utf-16"?><testMessage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" name="TestMessage" sendFrom="NodeA" sendTo="NodeA" soureClient="capp" hide=""><test>MessagetOSend</test></testMessage>"""
    oneiroi=None
    def handelOneiroi(self,oneiroi):    
        OneiroiHandler.oneiroi.connect_to_Daemon()
        OneiroiHandler.oneiroi.keep_listening()
    def __init__(self,_daemonURL,CleintID):
        if not OneiroiHandler.oneiroi:
            OneiroiHandler.clientName=CleintID
            OneiroiHandler.daemonURL=_daemonURL
            OneiroiHandler.oneiroi=OneiroiConnection(OneiroiHandler.clientName,OneiroiHandler.daemonURL)
            oneiroiThread=Thread(target=self.handelOneiroi,args=(OneiroiHandler.oneiroi,))
            oneiroiThread.start()            
            time.sleep(2)    
    def Connect_TO_Node(self,NodeName,MessageHandler):
        OneiroiHandler.NodeConnections[NodeName]=MessageHandler
        OneiroiHandler.oneiroi.connect_To_Node(NodeName,MessageHandler)
    def Setup_Attribute_Notification(self,NodeName,AttributeName):
        if OneiroiHandler.NodeConnections[NodeName]:
            OneiroiHandler.oneiroi.Set_Node_Attribute_Notification(NodeName,AttributeName)
    def Subscribe_To_Node_Message(self,NodeName):
        if OneiroiHandler.NodeConnections[NodeName]:
            OneiroiHandler.oneiroi.Subscribe_To_Node_Messages(NodeName)
    def UnSubscribe_From_NodeMessages(self,NodeName):
        if OneiroiHandler.NodeConnections[NodeName]:
            OneiroiHandler.oneiroi.unsubscribe_From_Node_Message(NodeName)
    def Set_Node_Attribute_Value(self,NodeName,AttributeName,AttributeValue):
        if OneiroiHandler.NodeConnections[NodeName]:
            OneiroiHandler.oneiroi.Set_Attribute_Value(NodeName,AttributeName,AttributeValue)
    def Get_Node_Attribute_Value(self,NodeName,AttributeName):
        if OneiroiHandler.NodeConnections[NodeName]:
            OneiroiHandler.oneiroi.get_Attribute_value(NodeName,AttributeName)
    def Send_Message(self,xmlMessage):
        if OneiroiHandler.NodeConnections[NodeName]:
            OneiroiHandler.oneiroi.Send_Message(xmlMessage)
    def create_Node_Implementation(self,NodeName):       
        currentNodeDefinition=OneiroiHandler.oneiroi.get_Node_Structure(NodeName)      
        if currentNodeDefinition:
            fileName=NodeName+'_Impl1.py'
            f= open(fileName,"w+")
            dt=str(datetime.datetime.now())
            f.write("##becos Oneiroi Node Implementation\n")
            f.write(f"##Auto Generated:{dt} \n\n")

            f.write("from becosOneiroi import OneiroiHandler\n")
            f.write("from becosOneiroi import oneiroiReceiver\n")
            f.write("import xml.etree.ElementTree as xmlParser\n")
            f.write(f"class {NodeName}_Impl(oneiroiReceiver):\n")
            f.write("\tdaemonURL="+f"'{self.daemonURL}'\n")
            f.write("\tclientName="+f"'{self.clientName}'\n")
            f.write("\tconHandler=OneiroiHandler(daemonURL,clientName)\n")
            for attribute in currentNodeDefinition['allAttributes']:
                f.write(f"\t{attribute['attributeName']}=None\n")
            f.write("\tdef OnResponse(self,message):\n") 
            f.write("\t\tprint(message)\n") 
            f.write("\tdef OnNodeResponse(self,NodeName,message):\n") 
            f.write("\t\tprint(f'NodeName:{NodeName},message{message}')\n") 
            f.write("\tdef OnMessageReceived(self,messageID,NodeName,XmlMessage):\n")
            f.write("\t\tres=xmlParser.fromstring(XmlMessage)\n")
            f.write("\t\tmessageType=res.attrib['name']\n")
            for messagebinding in currentNodeDefinition['allMessageBindings']:
                if messagebinding['MessageFlow'].lower()=='inbound':
                    f.write(f"\t\tif messageType.lower()=='{messagebinding['MessageType'].lower()}':\n")
                    f.write(f"\t\t\tself.on_{messagebinding['MessageType'].lower()}_Received(XmlMessage)\n")
            f.write("\tdef OnAttributeValueReceived(self,Client,NodeName,AttributeName,AttributeValue):\n")
            f.write("\t\tprint('')\n")
            for attribute in currentNodeDefinition['allAttributes']:
                f.write(f"\t\tif(AttributeName=='{attribute['attributeName']}'):\n")
                f.write(f"\t\tself.{attribute['attributeName']}=AttributeValue\n")
            f.write("\tdef __init__(self):\n")
            f.write(f"\t\tself.conHandler.Connect_TO_Node('{NodeName}',self)\n")
            f.write(f"\t\tself.conHandler.Subscribe_To_Node_Message('{NodeName}')\n")
            for attribute in currentNodeDefinition['allAttributes']:
                if attribute['isNotifiable']==True:
                    f.write(f"\t\tself.conHandler.Setup_Attribute_Notification('{NodeName}','{attribute['attributeName']}')\n")
            for attribute in currentNodeDefinition['allAttributes']:
                f.write(f"\tdef set_{attribute['attributeName']}(self,newValue):\n")
                f.write(f"\t\tself.conHandler.Set_Node_Attribute_Value('{NodeName}','{attribute['attributeName']}',newValue)\n")
            for messagebinding in currentNodeDefinition['allMessageBindings']:
                if messagebinding['MessageFlow'].lower()=='inbound':
                    f.write(f"\tdef on_{messagebinding['MessageType'].lower()}_Received(self,xmlMessage):\n")
                    f.write(f"\t\t##message Handling\n")
                    f.write(f"\t\tprint(xmlMessage)\n")
                else:
                    f.write(f"\tdef send_{messagebinding['MessageType'].lower()}(self,xmlMessage):\n")
                    f.write(f"\t\tself.conHandler.Send_Message(xmlMessage)\n")
            f.close()
            return True
        else:
            return False

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
        self.daemonURL=oneiroi_daemonURL+'signalr'       
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

class oneiroiReceiver(ABC):
    @abstractmethod
    def OnResponse(self,message):
        pass
    @abstractmethod
    def OnNodeResponse(self,NodeName,message):
        pass
    @abstractmethod
    def OnMessageReceived(self,messageID,NodeName,Message):
        pass
    @abstractmethod
    def OnAttributeValueReceived(self,Client,NodeName,AttributeName,AttributeValue):
        pass