from _thread import start_new_thread
from threading import Thread
import threading
import asyncio
import time
from OneiroiConnection import OneiroiConnection
import datetime
from time import gmtime, strftime
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
            f.write("from oneiroiReceiver import oneiroiReceiver\n")
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
            f.write("\t\tprint('')")
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