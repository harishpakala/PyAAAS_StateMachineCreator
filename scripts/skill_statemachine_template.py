"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: {{MetaData/Author}}
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
from datetime import datetime

try:
    import queue as Queue
except ImportError:
    import Queue as Queue 

import json
import logging
import random
import sys
import time
import uuid

try:
    from utils.i40data import Generic
except ImportError:
    from main.utils.i40data import Generic

try:
    from utils.aaslog import serviceLogHandler,LogList
except ImportError:
    from main.utils.aaslog import serviceLogHandler,LogList

'''
    The skill generator extracts all the states from the transitions list.
    For each STATE, a seperate python class is created. This python class has two main
    functions run() and the next(). The run method is required to execute a set
    of instructions so that the class which represents a state could exhibit a specific behavior. 
    The next method defines the next class that has to be executed.
    
    Each transition is attributed by input document and outpput document.
    
    In the case of  input document, the class is expected to wait for the 
    arrival of a specific document type. While for the output document, the class
    is expected to send out the output document.
    
    This source-code consists of a base class and the all the classes each pertaining 
    to definite state of the skill state-machine. The base class represents the skill 
    and coordinates the transition from one state to another.
    
    The baseclass is responsible for collecting the documents from the external
    world (either from other skill that is part of the AAS or a skill part of 
    of another AAS). For this the baseclass maintains a queue one for each class. 
    
    The communication between any two skills of the same AAS or the skills of 
    different AAS is done in I4.0 language.
    
    An I4.0 message packet consists of a frame header and the interactionElements
    detail part. The frame element consists of Sender and Receiver elements. Under
    this the AASID's and respective skillnames can be specified.
    
    Also  every message packet is associated with a type, the type information is 
    specified in the Input and Output property tags under Transition collection in
    the AASx package.
    
    Based on the receive information in the frame header, the message is routed appropriate
    Skill. The base-class maintains a specific InboundQueue, into the messages dropped by the
    messagehandler. 
    
    A class specific inbound queue is defined in the baseclass for the classes defined in this
    source-code. A dictionary is also manitained, with key representing the messagetype and the
    value being the class specific inboundqueue.
    
    Every inbound message to the skill, is routed to the specific class based on its message type
    from the base CLaas.  
    
    For operational purposes, a dictionary variable is defined for each message type that this skill
    expects. 

    StateName_In         
    StateName_Queue 
        
    The sendMessage method in the baseclass submits an outbound message to the message handler so that
    it could be routed to its destination. Every class can access this method and publish the outbound
    messgae.  
    
    Accessing the asset entry within a specific class
        For accessing the asset, a developer has to write specific modules in the assetaccessadaptors
        package. In this version of LIAPAAS framework PLC OPCUA adaptor for reading and writing OPCUA
        variables is provided.
        
        The asset access information like IP address, port, username, password and the opcua variables
        are defined in the AASx configuration file.
        
        The module and the related OPCUA variable definitions with thin the skill.
        
        MODULE_NAME = "PLC_OPCUA"
        #Accessing the specifc assetaaccess adaptor 
        self.plcHandler = self.base_class.pyaas.assetaccessEndpointHandlers[MODULE_NAME] # 1
        
        #accessing the list property variables Dictionary are specified in the configuration file.  
        self.propertylist = self.base_class.shellObject.thing_description
        
        PLC_OPCUA represents the module specific to opcua adaptor to access the PLC
        
        The code snippets 1 and 2 need to be initialized in the constructor of the class        
        
    def StateName_Logic(self):
        self.plcHandler.read(self.propertylist["sPermission"])
        self.plcHandler.write(self.propertylist["sPermission"],"value")
        time.sleep(10)
      
       The propertylist is the dictionary, that has asset specific keys *OPCUA variables and the respective
        addresses.
    
    creating an outbound I40 message.
    
    Note : The communication between the skills that are part of the same AAS, or different
    AAS should happen within the I40 data format structure.
    
    A generic class is provided within the package utils.i40data (it is imported in the code).
    
    code snippet
    
    self.gen = Generic()
    self.frame = self.gen.createFrame(I40FrameData)
    
    
    If the receiver is a skill within the same AAS, the ReceiverAASID would be same as SenderAASID
    where the ReceiverRolename would be specific skill Name 
    
    The ReceiverAASID and ReceiverRolename could be obtained from sender part of the incoming message
    and these are to be provided empty, if there is no receiver.
    receiverId = self.base_class.StateName_In["frame"]["sender"]["identification"]["id"]
    receiverRole = self.base_class.StateName_In["frame"]["sender"]["role"]["name"]
    
    I40FrameData is a dictionary
    
    language : English, German
    format : Json, XML //self.base_class.pyaas.preferredCommunicationFormat
    reply-to : HTTP,MQTT,OPCUA (endpoint) // self.base_class.pyaas.preferedI40EndPoint
    serviceDesc : "short description of the message"

        {
        "type" : ,
        "messageId":messageId,
        "SenderAASID" : self.base_class.aasID,
        "SenderRolename" : "{{MetaData/Name}}",
        "conversationId" : "AASNetworkedBidding",
        "replyBy" :  "",   # "The communication protocol that the AAS needs to use while sending message to other AAS."
        "replyTo" : "",    # "The communication protocol that the receipient AAS should use for reply"   
                           # In case the message needs to be routed to another skill please "Internal"
        "ReceiverAASID" :  receiverId,
        "ReceiverRolename" : receiverRole,
        "params" : {},
        "serviceDesc" : "",
        "language" : "",
        "format" : ""  
    } # In proposal needs to be confirmed
    
    the interactionElements part of the I40 frame usually contain the submodel elements,
    the respective the submodel element could be fetched from the submodel dictionary.
    
    The fetching of the submodel elements is done dynamically from the database.
    
    example Boring (should be same as the one specified in AASX file.)
    boringSubmodel = self.base_class.pyaas.dba.getSubmodelsbyId("BoringSubmodel")
    # result is list
    I40OutBoundMessage = {
                            "frame" : frame,
                            "interactionElements" : boringSubmodel
                        }
                        
    Saving the inbound and outbound messages into the datastore
    
    example :
    
    def retrieveMessage(self):
        self.base_class.StateName_In = self.base_class.StateName_Queue.get()
    
    def saveMessage(self):
        inboundQueueList = list(self.base_class.StateName_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.base_class.StateName_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "message":message})
        
    
'''
    
{{#each StateANDTransitionList}}
class {{StateName}}:
    
    def __init__(self, base_class):
        '''
        '''
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        {{#each ConditionList}}
        self.{{targetstate}}_Enabled = True
        {{/each}}
    
    {{#each IDCYes}}
    def retrieve_{{StateName}}_Message(self) -> None:
        self.base_class.{{StateName}}_In = self.base_class.{{StateName}}_Queue.get()
    
    def saveMessage(self) -> None:
        inboundQueueList = list(self.base_class.{{StateName}}_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.base_class.{{StateName}}_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "message":message})
            
    {{/each}}

    def {{StateName}}_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    {{#each ODCYes}}
    def create_Outbound_Message(self) -> List():
        self.oMessages = "{{oMessage}}".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.{{StateName}}_In
            self.gen = Generic()
            #receiverId = "" # To be decided by the developer
            #receiverRole = "" # To be decided by the developer
            
            # For broadcast message the receiverId and the 
            # receiverRole could be empty 
            
            # For the return reply these details could be obtained from the inbound Message
            receiverId = message["frame"]["sender"]["identification"]["id"]
            receiverRole = message["frame"]["sender"]["role"]["name"]
            
            # For sending the message to an internal skill
            # The receiver Id should be
            
            I40FrameData =      {
                                    "semanticProtocol": self.base_class.semanticProtocol,
                                    "type" : oMessage,
                                    "messageId" : oMessage+"_"+str(self.base_class.pyaas.dba.getMessageCount()[0]+1),
                                    "SenderAASID" : self.base_class.pyaas.aasID,
                                    "SenderRolename" : self.base_class.skillName,
                                    "conversationId" : message["frame"]["conversationId"],
                                    "replyBy" :  self.base_class.pyaas.lia_env_variable["LIA_PREFEREDI40ENDPOINT"],
                                    "replyTo" :  message["frame"]["replyBy"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            oMessage_Out = {"frame": self.frame}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            
            #self.InElem = self.base_class.pyaas.dba.getSubmodelsbyId({"aasId":self.base_class.pyaas.aasID,"submodelId":"BoringSubmodel"})
            #oMessage_Out ={"frame": self.frame,
            #                        "interactionElements":self.InElem["message"]}
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "message":oMessage_Out})
            outboundMessages.append(oMessage_Out)
        return outboundMessages
    {{/each}}
    
    def run(self) -> object:
            
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: {{StateName}}")
        # InputDocumentType"
        InputDocument = "{{InMessageList}}"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        {{#each IDCYes}}
        '''
            In case a class expects an input document then.
            It would need to lookup to its specific queue
            that is defined in the based class
        '''
        if (InputDocument != "NA"):
            self.messageExist = True
            i = 0
            sys.stdout.write(" Waiting for response")
            sys.stdout.flush()
            while (((self.base_class.{{StateName}}_Queue).qsize()) == 0):
                time.sleep(1)
                i = i + 1 
                if i > 10: # Time to wait the next incoming message
                    self.messageExist = False # If the waiting time expires, the loop is broken
                    break
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_{{StateName}}_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        {{/each}}
        self.{{StateName}}_Logic()
        
    def next(self) -> object:
        OutputDocument = "{{OutputDocument}}"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        {{#each ODCYes}}
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.base_class.sendMessage(outbMessage)
        {{/each}}
        
        {{#each ConditionList}}
        if (self.{{targetstate}}_Enabled):
            self.base_class.skillLogger.info("Condition :" + "{{Condition}}")
            ts = {{targetstate}}(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        {{/each}}
        
{{/each}}


{{#each ExitState}}
class Exit:
    
    def __init__(self, base_class):
        '''
        '''
        self.base_class = base_class
        self.I40OutBoundMessage = {}
        
    def run(self) -> None:
            
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: Exit")
        # InputDocumentType"
        '''
            In case a class expects an input document then.
            It would need to lookup to its specific queue
            that is defined in the based class
        '''

    def next(self) -> None:
        '''
                  If the condition is soecified is specified as '-' in the config file
                  please replace it with the needed condition usually True or False
        '''
        if (True):
            self.base_class.skillLogger.info("Condition :" + "-")
            self.base_class.skillLogger.info("############################################################################# \n")
            return None
{{/each}}        

class {{MetaData/Name}}:
    '''
    classdocs
    '''

        
    def initstate_specific_queue_internal(self) -> None:
        """
        """
        self.QueueDict = {}
        
        {{# each StateANDTransitionList}}
        self.{{StateName}}_Queue = Queue.Queue()
        {{/each}}
        
                
        self.QueueDict = {
            {{#each IDCList}}
              "{{IDC}}": self.{{StateName}}_Queue,
            {{/each}}
            }
    
    def init_inbound_messages(self) -> Nones:
        {{#each InputMessageTypeList}}
        self.{{StateName}}_In = {}
        {{/each}}
        pass
    
    def empty_all_queues(self) -> None:
        for queueName,queue in self.QueueDict.items():
            queueList = list(self.queue.queue)
            for elem in range(0,len(queueList)):
                queue.get()
    
    def create_status_message(self) -> None:
        self.StatusDataFrame =      {
                                "semanticProtocol": self.semanticProtocol,
                                "type" : "StausChange",
                                "messageId" : "StausChange_1",
                                "SenderAASID" : self.aasID,
                                "SenderRolename" : self.skillName,
                                "conversationId" : "AASNetworkedBidding",
                                "replyBy" :  "",
                                "replyTo" :"",
                                "ReceiverAASID" :  self.aasID + "/"+self.skillName,
                                "ReceiverRolename" : "SkillStatusChange"
                            }
        self.statusframe = self.gen.createFrame(self.StatusDataFrame)
        self.statusInElem = self.pyaas.aasConfigurer.getStatusResponseSubmodel()
        self.statusMessage ={"frame": self.statusframe,
                                "interactionElements":[self.statusInElem]}
 
    
    def __init__(self,pyaas):
        '''
        Constructor
        '''
        
        self.SKILL_STATES = {
                        {{#each StatesList}}  "{{StateName}}": "{{StateName}}",{{/each}}
                       }
        
        self.pyaas = pyaas
        self.skillName = "{{MetaData/Name}}"
        self.initstate_specific_queue_internal()
        self.init_inbound_messages()
        self.currentConversationId = "temp"
        
        self.enabledStatus = {"Y":True, "N":False}
        self.enabledState = self.enabledStatus["{{MetaData/enabled}}"]
        
        self.semanticProtocol = "{{MetaData/MetaData/semanticProtocol}}"
        self.initialState = "{{MetaData/InitialState}}"
        self.skillservice = "{{MetaData/SkillService}}"
        self.gen = Generic()
        self.createStatusMessage()
        self.productionStepSeq = []
        self.responseMessage = {}
        
    def start(self, msgHandler,uuid ,shellObject,_uid) -> None:
        """
            Starting of the Skill state machine
        """
        self.msgHandler = msgHandler
        self.skillDetails = skillDetails
        self.shellObject = shellObject
        self.aasID = shellObject.aasELement["id"]
        self.aasID = aasID
        self.uuid  = uuid
        self.skillLogger = logging.getLogger(self.aasID+"."+self.skillName)
        self.skillLogger.setLevel(logging.DEBUG)
        
        self.commandLogger_handler = logging.StreamHandler(stream=sys.stdout)
        self.commandLogger_handler.setLevel(logging.DEBUG)
        
        self.fileLogger_Handler = logging.FileHandler(self.pyaas.base_dir+"/logs/"+"_"+str(self.uuid)+"_"+self.skillName+".LOG")
        self.fileLogger_Handler.setLevel(logging.DEBUG)
        
        self.listHandler = ServiceLogHandler(LogList())
        self.listHandler.setLevel(logging.DEBUG)
        
        self.Handler_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
        
        self.listHandler.setFormatter(self.Handler_format)
        self.commandLogger_handler.setFormatter(self.Handler_format)
        self.fileLogger_Handler.setFormatter(self.Handler_format)
        
        self.skillLogger.addHandler(self.listHandler)
        self.skillLogger.addHandler(self.commandLogger_handler)
        self.skillLogger.addHandler(self.fileLogger_Handler)
        
        self.skillDetails = skillDetails
        {{InitialState}}_1 = {{InitialState}}(self)
        self.stateChange("{{InitialState}}")
        currentState = {{InitialState}}_1
        self.enabledState = self.skillDetails["enabled"]
        
        
        while (True):
            if ((currentState.__class__.__name__) == "{{InitialState}}"):
                if(self.enabledState):
                    currentState.run()
                    ts = currentState.next()
                    self.stateChange(ts.__class__.__name__)
                    currentState = ts
                else:
                    time.sleep(1)
            else:
                currentState.run()
                ts = currentState.next()
                if not (ts):
                    break
                else:
                    self.stateChange(ts.__class__.__name__)
                    currentState = ts
    
    def geCurrentSKILLState(self) -> str:
        return self.SKILL_STATE
    
    def getListofSKILLStates(self) -> List():
        return self.SKILL_STATES
    
    
    def stateChange(self, STATE) -> None:
        self.statusMessage["interactionElements"][0]["submodelElements"][0]["value"] = "I"
        self.statusMessage["interactionElements"][0]["submodelElements"][1]["value"] = "A006. internal-status-change"
        self.statusMessage["interactionElements"][0]["submodelElements"][2]["value"] = str(datetime.now()) +" "+STATE
        #self.sendMessage(self.statusMessage)
    
    def sendMessage(self, sendMessage) -> None:
        self.msgHandler.putObMessage(sendMessage)
    
    def receiveMessage(self,inMessage) -> None:
        try:    
            _conversationId = str(inMessage['frame']['conversationId'])
            senderRole = str(inMessage["frame"]['sender']['role']["name"])
            _messageType = str(inMessage['frame']['type'])
            self.QueueDict[_messageType].put(inMessage)
        except Exception as E:
            pass#self.skillLogger.info("Raise an Exception " + str(E))



if __name__ == '__main__':
    
    lm2 = {{MetaData/Name}}()
    lm2.Start('msgHandler')
