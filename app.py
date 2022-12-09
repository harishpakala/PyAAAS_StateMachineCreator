'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''

from flask_restful import Api,Resource,request
from flask import render_template,Response,redirect,make_response,Flask,flash

import io
from io import StringIO
import json
import logging
import os

from statemachinegenerate import StatMachineGenerator


flask_app = Flask(__name__)
flask_app.secret_key = os.urandom(24)
flask_app.config["UPLOAD_PATH"] = "/"
pyAAS_webKit_api = Api(flask_app)
flask_app.logger.disabled = True
log = logging.getLogger('AAS State Machine Creator WEBAPI')
log.setLevel(logging.ERROR)
log.disabled = True

class Generation(Resource):
    def __init__(self,script_dir):
        self.script_dir = script_dir
        self.stateMachineData = {}
        
    def retrieveAASData(self,request):
        try:
            f = io.TextIOWrapper(request.files['file'])
            fileName = request.files["file"].filename
            self.aasxZipFolder = "Test_config"#fileName.split(".aasx")[0]
            aasxData = json.load(request.files["file"])
            self.stateMachineData = {"fileName":fileName,"statemachine":aasxData}
            return True
        except Exception as E:
            print("Error while extracting the file "+ str(E))
            return False
        
    def post(self):
        try:
            formVariables = request.form
            if (self.retrieveAASData(request)):
                try:
                    smg = StatMachineGenerator(self.stateMachineData["statemachine"])
                    smg.preProcessStateMachineDATA()
                    stateMachineCodeSinppet = smg.codeGenerator(self.stateMachineData["fileName"])
                    print("Code generation is success")
                    _fileName = (self.stateMachineData["statemachine"]["MetaData"]["Name"])
                    with StringIO() as buffer:
                        buffer = StringIO()
                        buffer.write(str(stateMachineCodeSinppet))
                        response = make_response(buffer.getvalue())
                        response.headers['Content-Disposition'] = "attachment;  filename="+_fileName+".py"
                        response.mimetype = 'text/plain-text'
                        return response
                except Exception as E:
                    print(str(E))
                    flash("Unexpected Internal Server Error " + str(E),"error")
                    return redirect(("/"))
            else:
                flash("The json file is not properly formatted","error")
                return redirect(("/"))
                        
        except Exception as E:
            flash("Unexpected Internal Server Error" + str(E),"error")
            return redirect(("/"))

    def get(self):
        try:
            return Response(render_template('index.html'))
        except Exception as E:
            print("error at Generation Get REST API ", str(E))
            return "Unexpected Internal Server error"

class PyAASWebKit(object):
    
    def __init__(self,):
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        pyAAS_webKit_api.add_resource(Generation, "/", resource_class_args=tuple([self.script_dir]))

    
    def start(self):
        flask_app.run(host="0.0.0.0",port=50008)
        
if __name__ == '__main__':
    pwK = PyAASWebKit()
    pwK.start()