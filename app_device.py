#!/usr/bin/env python
#coding= utf-8

from ConsoleThreading import *
from flask import Flask, render_template, Response, request, redirect, json, jsonify, abort

app = Flask(__name__)
Model='Web2uart Control'
nameing = [{"id": 1, "name": "CHIPS", "done": False}, {"id": 2, "name": "garden", "done": False}]  #json

def CheckSerial():
    #Serial = SerialTask('/dev/ttyAMA0',115200)	#test Slave of the PC station control
    #Serial = SerialTask('/dev/ttyUSB0',115200)	#test Master of ipad myself
    Serial = SerialTask('/dev/ttyUSB0',9600)	#test Master of BK5491B
    #Serial = SerialTask('/dev/ttyACM0',115200)	#test Master of PSW 80-13.5 power supply
    if Serial.isopen():	
        task = Thread(target=Serial.run, args=('for_serial_class',))	#開啟Allocate threading function
        task.start()	#啟動
    return Serial

#==========================================================================
# Run Raspberry Pi
#==========================================================================
@app.route('/model', methods = ['GET'])    #like model for automatic control
def model():
    lines= Model+'</br>'
    return Response(lines, mimetype='text/html')

@app.route('/version', methods = ['GET'])
def version():
    Serial=CheckSerial()
    if Serial.isOpen():
        message='*IDN?\n'
        Serial.send(message)
        time.sleep(0.1)
        print '\r%s'%Serial.receive()
        lines=Serial.receive()
    else:
        lines='Check serial port'
    Serial.terminate()
    lines=lines.replace('\n','</br></br>')  #to text/html
    return Response(lines, mimetype='text/html')

@app.route('/getjson', methods = ['GET'])
def get_json():
    return json.dumps(nameing)
    #return jsonify(nameing)            #異曲同工

@app.route('/setjson/<int:id>', methods=['GET'])
def set_json(id=1):
    task = filter(lambda t: t['id'] == id, nameing)
    if len(task) == 0:
        abort(404)
    return jsonify(task[0])             #符合之項目
    #return jsonify({'task': task[0]})  #符合之項目之數組
    #return json.dumps({'id':id})

@app.route('/postset/<int:id>/<name>', methods = ['POST','GET'])   #GET for debug
def post_set(id,name):
    task = {
        "id": nameing[-1]['id'] + 1,
        "name": name,
        "done": False
    }
    nameing.append(task)
    #return jsonify(nameing)
    return jsonify({'nameing': nameing})

@app.route('/postjson', methods = ['POST','GET'])   #GET for debug
def post_json(name='L'):
    if not request.json:    #have josn body
        abort(400)
    task = {
        "id": nameing[-1]['id'] + 1,
        "name": request.json['name'],   #根據Client request {"name": "xxxx"}
        "done": False
    }
    nameing.append(task)
    return jsonify(nameing)    
    #[{"id":1,"name":"CHIPS"},{"id":2,"name":"garden"},{"id":3,"name":"L"}]

    #return jsonify({'nameing': nameing})    
    #{"nameing":[{"id":1,"name":"CHIPS"},{"id":2,"name":"garden"},{"id":3,"name":"L"}]}

