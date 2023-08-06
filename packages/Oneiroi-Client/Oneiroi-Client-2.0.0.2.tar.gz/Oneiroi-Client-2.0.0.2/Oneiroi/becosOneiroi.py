from _thread import start_new_thread
from threading import Thread
import threading
import asyncio
import time
from OneiroiConnection import OneiroiConnection
class OneiroiHandler:
    daemonURL=None
    clientName=None
    messageText = """<?xml version="1.0" encoding="utf-16"?><testMessage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" name="TestMessage" sendFrom="NodeA" sendTo="NodeA" soureClient="capp" hide=""><test>MessagetOSend</test></testMessage>"""
    oneiroi=None
    def handelOneiroi(self,oneiroi):    
        oneiroi.connect_to_Daemon()
        oneiroi.keep_listening()
    def __init__(self,_daemonURL,CleintID,Receiver):
        self.clientName=CleintID
        self.daemonURL=_daemonURL
        self.oneiroi=OneiroiConnection(self.clientName,self.daemonURL,Receiver)
        oneiroiThread=Thread(target=self.handelOneiroi,args=(self.oneiroi,))
        oneiroiThread.start()
        time.sleep(5)
    def Connect_TO_Node(self,NodeName):
        self.oneiroi.connect_To_Node(NodeName)
    def Setup_Attribute_Notification(self,NodeName,AttributeName):
        self.oneiroi.Set_Node_Attribute_Notification(NodeName,AttributeName)
    def Subscribe_To_Node_Message(self,NodeName):
        self.oneiroi.Subscribe_To_Node_Messages(NodeName)
    def UnSubscribe_From_NodeMessages(self,NodeName):
        self.oneiroi.unsubscribe_From_Node_Message(NodeName)
    def Set_Node_Attribute_Value(self,NodeName,AttributeName,AttributeValue):
        self.oneiroi.Set_Attribute_Value(NodeName,AttributeName,AttributeValue)
    def Get_Node_Attribute_Value(self,NodeName,AttributeName):
        self.oneiroi.get_Attribute_value(NodeName,AttributeName)
    def Send_Message(self,xmlMessage):
        self.oneiroi.Send_Message(xmlMessage)