"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: {{MetaData/Author}}
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""

try:
    import queue as Queue
except ImportError:
    import Queue as Queue 
try:
    from utils.utils import Actor,AState
except ImportError:
<<<<<<< HEAD
    from main.utils.utils import Actor,AState
=======
    from src.main.utils.i40data import Generic

try:
    from utils.aaslog import ServiceLogHandler,LogList
except ImportError:
    from src.main.utils.aaslog import ServiceLogHandler,LogList
>>>>>>> 2f0e267f7f039a9819f9fe5c32602efef5f1fad3

'''

'''    
{{#each StateANDTransitionList}}
class {{StateName}}(AState):
    
    def initialize(self):
        self.InputDocument = "{{InMessageList}}"
        self.OutputDocument = "{{OutputDocument}}"
        {{#each IDCYes}}
        self.in_queue = self.base_class.{{StateName}}_Queue
        self.base_class.{{StateName}}_In = self.message
        {{/each}}
        # Gaurd variables for enabling the transitions
        {{#each ConditionList}}
        self.{{targetstate}}_Enabled = True
        {{/each}}
<<<<<<< HEAD
=======
    
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
    def create_Outbound_Message(self) -> list:
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
>>>>>>> 2f0e267f7f039a9819f9fe5c32602efef5f1fad3
        
    {{#each ODCYes}}
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.{{StateName}}_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    {{/each}}
    
    def actions(self) -> None:
        {{#if IDCYes}}
        {{#each IDCYes}}
        if (self.wait_untill_timer(1,10)):
            self.receive()
            self.save_in_message(self.message)
        {{/each}}
        {{else}}
        pass
        {{/if}}
        
    def transitions(self) -> object:
        {{#each ODCYes}}
        self.send(self.create_outbound_message())
        {{/each}}
        {{#each ConditionList}}
        if (self.{{targetstate}}_Enabled):
            ts = {{targetstate}}(self.base_class,"{{targetstate}}")
            return ts
        {{/each}}
        
{{/each}}


{{#each ExitState}}
class Exit(AState):
    
    def initialize(self):
        """
            This the generic state class this used when the state machine
            is to be exited.
        """
        pass
    
    def actions(self) -> None:
        pass    
        
    def transitions(self) -> None:
        '''
                  If the condition is soecified is specified as '-' in the config file
                  please replace it with the needed condition usually True or False
        '''
        if (True):
            self.log_info("Condition :" + "-")
            self.log_info("############################################################################# \n")
            return None
{{/each}}        

class {{MetaData/Name}}(Actor):
    '''
    classdocs
    '''

        
    def initstate_specific_queue_internal(self) -> None:
        """
        """
        self.QueueDict = dict()
        
        {{# each IDCList}}
        self.{{StateName}}_Queue = Queue.Queue()
        {{/each}}
        
                
        self.QueueDict = {
            {{#each IDCList}}
              "{{IDC}}": self.{{StateName}}_Queue,
            {{/each}}
            }
    
    def init_inbound_messages(self) -> None:
        {{#each InputMessageTypeList}}
        self.{{StateName}}_In = None
        {{/each}}
        pass
    
    def __init__(self,pyaas):
        '''
        Constructor
        '''
        self.SKILL_STATES = {
                        {{#each StatesList}}  "{{StateName}}": "{{StateName}}",{{/each}}
                       }
<<<<<<< HEAD

        Actor.__init__(self,pyaas,"{{MetaData/Name}}",
                       "{{MetaData/semanticProtocol}}",
                       "{{MetaData/SkillService}}","{{InitialState}}")

                
    def start(self, msgHandler,shellObject,_uid) -> None:
=======
        
        self.pyaas = pyaas
        self.skillName = "{{MetaData/Name}}"
        self.initstate_specific_queue_internal()
        self.init_inbound_messages()
        self.currentConversationId = "temp"
        
        self.enabledStatus = {"Y":True, "N":False}
        self.enabledState = self.enabledStatus["{{MetaData/enabled}}"]
        
        self.semanticProtocol = "{{MetaData/semanticProtocol}}"
        self.initialState = "{{MetaData/InitialState}}"
        self.skill_service = "{{MetaData/SkillService}}"
        self.gen = Generic()
        self.create_status_message()
        self.productionStepSeq = []
        self.responseMessage = {}
        
    def start(self, msgHandler,uuid ,aasID) -> None:
>>>>>>> 2f0e267f7f039a9819f9fe5c32602efef5f1fad3
        """
            Starting of the Actor state machine
        """
<<<<<<< HEAD
        super().start( msgHandler,shellObject,_uid)
        
        {{InitialState}}_1 = {{InitialState}}(self,"{{InitialState}}")
        #self.stateChange("{{InitialState}}")
        self.currentState = {{InitialState}}_1
        self.InitialState = "{{InitialState}}"
        super().run(self.currentState,self.InitialState)
=======
        self.msgHandler = msgHandler
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
        
        self.create_status_message()
        {{InitialState}}_1 = {{InitialState}}(self)
        self.stateChange("{{InitialState}}")
        currentState = {{InitialState}}_1
        
        
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
    
    def getListofSKILLStates(self) -> list:
        return self.SKILL_STATES
    
    
    def stateChange(self, STATE) -> None:
        self.statusMessage["interactionElements"][0]["submodelElements"][0]["value"] = "I"
        self.statusMessage["interactionElements"][0]["submodelElements"][1]["value"] = "A006. internal-status-change"
        self.statusMessage["interactionElements"][0]["submodelElements"][2]["value"] = str(datetime.now()) +" "+STATE
        #self.sendMessage(self.statusMessage)
    
    def sendMessage(self, sendMessage) -> None:
        self.msgHandler.putObMessage(sendMessage)
>>>>>>> 2f0e267f7f039a9819f9fe5c32602efef5f1fad3
    
    def receiveMessage(self,inMessage) -> None:
        try:    
            _messageType = str(inMessage['frame']['type'])
            self.QueueDict[_messageType].put(inMessage)
        except Exception as E:
            pass



if __name__ == '__main__':
    
    lm2 = {{MetaData/Name}}()
    lm2.Start('msgHandler')
