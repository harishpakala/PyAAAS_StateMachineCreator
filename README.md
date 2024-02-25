# PyAAAS_StateMachineCreator
## Dependencies

This repository hosts the source code for State Machine Creator, 

:one: The  code is written in Python 3.9 <br />
:two: All the Python dependencies are specified in the [requirements.txt](https://github.com/harishpakala/PythonAASxServer/blob/master/requirements.txt) <br />
:three: The LIA OVGU development uses eclipse editor, accordingly eclipse related project files are provided in the repository.

### Installing Dependencies
<strong>pip3 install -r requirements.txt</strong> <br/>

## Running 
1) The base python program app.py is organized inside the root directory.  <br/>
<strong>python3.9 app.py</strong> <br/>

2) WEB UI for the state machine creator. The port number can be chaanged directly in the source-code app.py at the line no. 90
   <http://localhost:50008/>

## Create a new Finite State Machine
A Custom state-machine representation in json format is designed for creating the actual source-code. The sample state-machine representations are provided in the [examples sub-directory](https://github.com/harishpakala/PyAAAS_StateMachineCreator/tree/main/examples). 

![plot](./static/images/statemachinecreator_webui.png)
<p align="center">
The Web UI for the state machine creator
</p>

The JSON file needs to be upload via the ulpoad image button, once finished the generate button on the top needs to be clicked. In case the JSON file properly formatted the a python source code for the state machine represented will be downloaded automatically.

The generated python source-code needs to be placed in the sub-directory (src/main/skills) of the PythonAASxServer [source code](https://github.com/harishpakala/PythonAASxServer).

## Back Ground 
### Finite State Machines and the SKills.
<p align="justify">
In PythonAASxServer the concept skills represent the behavior of the type 3 AAS. These skills are modelled as Finite State Machines (FSM). The interactions between the skills happens with exchange the [I4.0 Messages](https://github.com/harishpakala/I40_Language_Semantics) <br/>
   
<strong>Interaction Protocols </strong> represent structured sequence of messages exchanged between multiple partners / actors to achieve a specified goal (Example : Three-Way Handhake Protocol). An instance / execution of an interaction protocol is associated with a specific conversationID, all the messages wihtin the concersation have the same conversationID within I4.0 frame part. Each skilll in a Interaction Protocol is specific Role Name. There could be multiple skills with same Role Name.<br/>

The Python source-code created by the state machine creator contains a set of classes. Each state represents a specific state and the entire state machine is represensted by anotehr class, that coordinates it's execution. <br/>

Each skill / FSM is associated with a specific queue within in the [PythonAASxServer](https://github.com/harishpakala/PythonAASxServer) framework.<br/>

Transitions between the states are expected due to one of the three event-types a) Inbound Message, b) Internal Trigger c) External Trigger.<br/>
</p>

## Sample State

```
class Hello(AState):
    message_in =  ["Ping",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.SendAck_Enabled = True 
            
    def actions(self) -> None:
        if (self.wait_untill_timeout(10)):
            message = self.receive(WaitforHi.message_in[0])
            self.save_in_message(message)
        
    def transitions(self) -> object:
        if (self.SendAck_Enabled):
            return "SendAck"
```

<p align="center">
A Hello state formatted as per Pyhton AASxServer and the StateMachine creator.
</p>

* The Hello state inherits the class Abstract class <strong>AState</strong> [source-code](https://github.com/harishpakala/PythonAASxServer/blob/c308300e3e78dbac5cacbbf6c09fc526a4d52eff/src/main/utils/sip.py#L43). <br/>
* The static variable message_in represents the list of messages that the FSM is expected to receive in the specific state. <br/>
* This class provides a set of guard conditions reequired for transitions to the next state. All the logic to the be executed within the Hello state needs to be written in the <strong>actions()</strong> method. <br/>
* The <strong>transitions()</strong> method should not be edited. <br/>
* For every next state a boolean guard variable will be provided in the constructor of the class, extracted from the JSON file. All the guard variables are defaulted to True. <br/>
* The developer needs to disable gaurd variable (False) in the <strong>actions()</strong> method, for the state that is not the next one. <br/>
* The [PythonAASxServer](https://github.com/harishpakala/PythonAASxServer) framework takes care and hide the complete mechanism behind the exchange of I4.0 messages between the skills. <br/>

### Send and Receive Methods 

```
receive(msg_in)
```
<p align="center">
Returns the first message from the inbound queue of type msg_in, if there is no message the method returns None.
</p>
<br/>

```
receive_all(msg_in)
```

<p align="center">
Returns all the messages from the inbound queue of type msg_in, if there is no message the method returns an empty list.
</p>
<br/>

### I4.0 Message creation Method  

```
create_i40_message(msg_out,conversationId,receiverId,receiverRole)
```
<p align="center">
Creates an I4.0 message of type 'msg_out' with a specific 'conversationId'. The senderRole will the SKill that has called this method. The receiverRole is destination skill.
The combination of receiverId and receiverRole is expected to be unique within the specific interaction. The senderId or the receiverId represents unique Id of the type3 AAS to which the SKill is attached.
</p>
<br/>

### Saving the I4.0 messages to the backend Methods

```
save_in_message(msg)
```
<p align="center">
Copies the contents of an inbound I4.0 messsage to backend.
</p>
<br/>

```
save_out_message(msg_in)
```

<p align="center">
Copies the contents of an outbound I4.0 messsage to backend.
</p>
<br/>

### AASx Data Access Methods

```
GetSubmodelById(submodelId)
```

<p align="center">
Returns the submodel of the specified submodelId. In case the submodel is not present or any internal error it returns error.
</p>
<br/>

```
GetSubmodelELementByIdshoortPath(submodelId)
```

<p align="center">
Returns the submodel-element of the specified submodelId and IdShortPath combination. In case the submodel-element is not present or any internal error it returns error.
</p>
<br/>

```
save_submodel(submodel)
```

<p align="center">
The replaces the existing submodel with the new submodel specified. Successful updation will return True, else returns False.
</p>
<br/>



### Predefined guard Methods

```
wait_untill_timeout(timer)
```
<p align="center">
The Control waits untill a specific number of seconds as assigned to argument to the method.
</p>
<br/>

```
wait_untill_message(message_count,msg_types)
```
<p>
The Control waits untill a specific number of messaages are arrived in the buffer of the message type specified as an argument msg_types (List of strings).
</p>
<br/>

```
wait_untill_message_timeout(message_count,timer,msg_types)
```
<p>
The Control waits untill a specific number of messaages are arrived in the buffer of the message type specified as an argument msg_types (List of strings). However if the timer expires, the control returns.
</p>
<br/>


## Issues
If you want to request new features or report bug [submit a new issue](https://github.com/harishpakala/PyAAAS_StateMachineCreator/issues/new)

## License

Python AAS Registry is Licensed under Apache 2.0, the complete license text including the copy rights is included under [License.txt](https://github.com/harishpakala/PythonAASxServer/blob/main/LICENSE.txt)

* Flask, Flask-RESTful, BSD-3-Clause <br />
* pybars3 GNU Lesser General Public License, Version 3 <br />
