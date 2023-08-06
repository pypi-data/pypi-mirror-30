from abc import ABC,abstractmethod

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

    


