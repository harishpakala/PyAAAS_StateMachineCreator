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
    from main.utils.utils import Actor,AState

{{#each StateANDTransitionList}}
class {{StateName}}(AState):
    {{#if IDCYes}}
    message_in =  {{#each InMessageList}}["{{this}}",]{{/each}}       
    {{/if}}
    {{#if OutputDocument_absent}}
    message_out =  {{#each OutMessageList}}["{{this}}",]{{/each}}
    {{/if}}
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        {{#each ConditionList}}
        self.{{targetstate}}_Enabled = True
        {{/each}}
            
    {{#each ODCYes}}
    def create_outbound_message(self,msg_type) -> list:
        receiverId =""
        receiverRole = ""
        conV1 = ""
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        #oMessage_Out["interactionElements"].append(submodel)
        self.save_out_message(oMessage_Out)
        return oMessage_Out
    {{/each}}
    
    def actions(self) -> None:
        {{#if IDCYes}}
        {{#each IDCYes}}
        if (self.wait_untill_timeout(10)):
            message = self.receive({{StateName}}.message_in[0])
            self.save_in_message(message)
        {{/each}}
        {{else}}
        pass
        {{/if}}
        
    def transitions(self) -> object:
        {{#each ODCYes}}
        self.send(self.create_outbound_message({{StateName}}.message_out[0]))
        {{/each}}
        {{#each ConditionList}}
        if (self.{{targetstate}}_Enabled):
            return "{{targetstate}}"
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

    def __init__(self):
        '''
        Constructor
        '''      
        Actor.__init__(self,"{{MetaData/Name}}",
                       "{{MetaData/semanticProtocol}}",
                       "{{MetaData/SkillService}}","{{InitialState}}")
                        

    def start(self):
        self.run("{{InitialState}}")


if __name__ == '__main__':
    
    lm2 = {{MetaData/Name}}()
    lm2.Start('msgHandler')
