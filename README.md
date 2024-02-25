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
A Custom state-machine representation in json format is designed for creating the actual source-code. The sample state-machine representations are provided (https://github.com/harishpakala/PyAAAS_StateMachineCreator/tree/main/examples). 

The Web UI 

![plot](./static/images/statemachinecreator_webui.png)


## Issues
If you want to request new features or report bug [submit a new issue](https://github.com/harishpakala/PyAAAS_StateMachineCreator/issues/new)

## License

Python AAS Registry is Licensed under Apache 2.0, the complete license text including the copy rights is included under [License.txt](https://github.com/harishpakala/PythonAASxServer/blob/main/LICENSE.txt)

* Flask, Flask-RESTful, BSD-3-Clause <br />
* pybars3 GNU Lesser General Public License, Version 3 <br />
