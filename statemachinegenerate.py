'''
Created on 29 Nov 2022

@author: pakala
'''
from pybars import Compiler
import os
import platform


class StateTransition(object):
    
    def __init__(self, StartState, InputDocument, Condition, OutputDocument, TargetState) :
        
        self.StartState = StartState
        self.InputDocument = InputDocument
        self.Condition = Condition
        self.OutputDocument = OutputDocument
        self.TargetState = TargetState
        
class StatMachineGenerator(object):
    
    def __init__(self,statemachineJSON):
        self.statemachineJSON = statemachineJSON
        self.processedJSON = {}
        self.finalDictJSON = {}
        self.platform = platform.system()
        base_dir = os.path.dirname(os.path.realpath(__file__))
        if self.platform == "Windows":
            self.skillTemplate = (base_dir) + "/scripts/skill_statemachine_template.py"
        elif self.platform == "Linux":
            self.skillTemplate = (base_dir) + "/../../"
        
    def preProcessStateMachineDATA(self):
        
        sMachine_dict = self.statemachineJSON

        TransitionsList = []
        statesListSet = set()
        inputMessageTypeSet = set()
        outputMessageTypeSet = set()
        for stateTransition in sMachine_dict['StateMachine']['Transitions']:
            st = StateTransition(str(stateTransition['StartState']), str(stateTransition['InputDocument']), str(stateTransition['Condition']),
                            str(stateTransition['OutputDocument']), str(stateTransition['TargetState']))
            
            statesListSet.add(str(stateTransition['StartState']))
            statesListSet.add(str(stateTransition['TargetState']))
            
            TransitionsList.append(st)
        statesListDict = []

        if "Exit" in statesListSet:
            self.finalDictJSON['ExitState'] = [{"Exit":"Yes"}]
        else :
            pass
        for state in statesListSet:
            stateDict = {}
            stateDict['StateName'] = state
            statesListDict.append(stateDict)
        
        stateandTransitionL = {}
        
        for state in statesListSet:
            temp = [] 
            for transition  in TransitionsList:
                if state == transition.StartState:
                    temp.append(transition)
            stateandTransitionL[state] = temp

        temp1 = []
        
        for state in stateandTransitionL.keys():
            try:
                tempDict = {}
                transitionList = stateandTransitionL.get(state)
                tempDict['InputDocument'] = transitionList[0].InputDocument
                
             
                tempDict['StateName'] = state
                tempDict['OutputDocument'] = transitionList[0].OutputDocument
                
                tempList1 = []
                iDListTemp =   []
                oDListTemp = []
                for tansit in transitionList:
                    tempDict1 = {}
                    if tansit.InputDocument != "NA":
                        iDListTemp.append({"IDC":tansit.InputDocument,
                                                        "StateName":state})
                       
                        inputMessageTypeSet.add(state)
                    if tansit.OutputDocument != "NA":
                        tempDict['OutputDocument_absent'] = True
                        outputMessageTypeSet.add(state)
                        oDListTemp.append({"ODC":tansit.OutputDocument,    
                                                         "StateName":state})
                    else:
                        tempDict['OutputDocument_absent'] = False
                    if ('sleep') in (tansit.Condition):
                        tempDict1['Condition'] = tansit.Condition + " == None"
                    elif tansit.Condition == "":
                        tempDict1['Condition'] = True
                    else:
                        tempDict1['Condition'] = tansit.Condition
                    tempDict1['targetstate'] = tansit.TargetState
                    tempList1.append(tempDict1)
                tempDict['ConditionList'] = tempList1
                tempDict["InDocumentCondition"] = iDListTemp
                tempDict["OutDocumentCondition"] = oDListTemp
                if len(iDListTemp) > 0 :
                    tempDict["IDCYes"] = [{"StateName":state}]
                    tList = []
                    for dict in iDListTemp:
                        tList.append(list(dict.values())[0])
                    tempDict['InMessageList'] = (list(set(tList)))
                    
                else:
                    tempDict["IDCYes"] = []
                    tempDict['InMessageList'] = []
                
                
                
                if len(oDListTemp) > 0 :
                    otList = []
                    for dict in oDListTemp:
                        otList.append(list(dict.values())[0])
                    otl = (list(set(otList)))
                    tempDict["ODCYes"] = [{"StateName":state,"oMessage": ' / '.join(otl)}]
                    tempDict['OutMessageList'] = (list(set(otList)))
                    
                else:
                    tempDict["ODCYes"] = []
                temp1.append(tempDict)
                
            except:
                pass
        self.finalDictJSON['InitialState'] = sMachine_dict['StateMachine']['InitialState']
        self.finalDictJSON['semanticProtocol'] = sMachine_dict['MetaData']['semanticProtocol']
        self.finalDictJSON['enabled'] = sMachine_dict['MetaData']['enabled']
        self.finalDictJSON['StateANDTransitionList'] = temp1
        IDCList  = []
        ODCList  = []
        in_messageTypeList = []
        out_messageTypeList = []
        for _temp1 in temp1:
            try:
                for idc in _temp1["InDocumentCondition"]:
                    if idc["IDC"] not in in_messageTypeList:
                        in_messageTypeList.append(idc["IDC"])
                        IDCList.append(idc)
            except Exception as e:
                pass
            try:
                for odc in _temp1["OutDocumentCondition"]:
                    if odc["ODC"] not in out_messageTypeList:
                        out_messageTypeList.append(odc["ODC"])
                        ODCList.append(odc)
            except Exception as e:
                pass

        metaData = sMachine_dict['MetaData']
        tempDict2 = {}
        tempDict2['Name'] = str(metaData['Name'])
        tempDict2['Author'] = str(metaData['Author'])
        tempDict2['Date'] = str(metaData['Date'])
        
        tempDict2['enabled'] = str(metaData['enabled'])
        tempDict2['semanticProtocol'] = str(metaData['semanticProtocol'])
        tempDict2['InitialState'] = str(sMachine_dict['StateMachine']['InitialState'])
        tempDict2['SkillService'] = str(metaData['SkillService'])
        
        self.finalDictJSON['MetaData'] = tempDict2
        self.finalDictJSON['StatesList'] = statesListDict
        self.finalDictJSON['IDCList'] = IDCList
        self.finalDictJSON['ODCList'] = ODCList
        
        inputMessageTypeDictList = []
        for eachEntry in inputMessageTypeSet:
            inputMessageTypeDictList.append({"StateName" : eachEntry })
        
        outputMessageTypeDictList = []
        for eachEntry in outputMessageTypeSet:
            outputMessageTypeDictList.append({"StateName" : eachEntry }) 
  
        self.finalDictJSON['InputMessageTypeList'] = inputMessageTypeDictList
        self.finalDictJSON['OutputMessageTypeList'] =  outputMessageTypeDictList

        
    def codeGenerator(self, filename):
        processedJSON = self.finalDictJSON
        
        compiler = Compiler()
        skillFile = os.path.join(filename)
        # Compile the template
        f = open(self.skillTemplate, "r")
        template = compiler.compile((f.read()))
        f.close()   
        
        # Render the template
        output = template((processedJSON))
        f.close()
        
        return output