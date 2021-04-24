#!/usr/bin/env python
#coding= utf-8

from ConsoleThreading import *
from flask import Flask, render_template, Response, request, redirect, jsonify
import json

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

@app.route('/getdata', methods = ['GET'])
def get_json():
    return json.dumps(nameing)
    #return jsonify(nameing)            #異曲同工

@app.route('/getset/<int:id>', methods=['GET'])
def set_json(id=1):
    task = filter(lambda t: t['id'] == id, nameing)
    if len(task) == 0:
        abort(404)
    return jsonify(task[0])             #符合之項目
    #return jsonify({'task': task[0]})  #符合之項目之數組
    #return json.dumps({'id':id})

@app.route('/getpost/<int:id>/<name>', methods = ['GET'])
def post_set(id,name):
    task = {
        "id": nameing[-1]['id'] + 1,
        "name": name,
        "done": False
    }
    nameing.append(task)
    return jsonify(nameing)
    #return jsonify({'nameing': nameing})    #會多了{ "nameing":[ {"done":True,"id":5,"name":"L"},{...}] }

@app.route('/postreturn', methods = ['POST'])   #GET for debug
def post_data(name='L'):
    print (request.headers)
    #print (request.data)
    print (request.get_data())
    #return Response("POST")     #for test
    #return Response(request.headers+request.data)
    return Response(str(request.headers)+request.get_data())
    #return Response(request.form.to_dict(), mimetype='text/html')
    #return Response(request.form.keys(), mimetype='text/html')
    #return Response(request.form.values(), mimetype='text/html')

    #return render_template(request.headers+request.data)
    #return render_template('post_submit.html')

@app.route('/postjson', methods = ['POST','GET'])   #GET for debug
def post_json(name='L'):
    print(request.headers)
    '''
    if not request.json:    #have josn body
        abort(400)
    '''
    if "application/json" in request.headers["Content-Type"]:   
        #body = request.json
        body = request.get_json()
        #print(json.dumps(request.get_json()))
        print('POST souce:\r\n%s'%body)
        print('POST json:\r\n%s'%json.dumps(body))
    else:
        #abort(400)     #只處理json body
        #body = request.data
        body = request.get_data()
        #print(json.loads(request.get_data(as_text=True)))
        #print('POST souce:\r\n%s'%body)
        print('POST body:\r\n%s'%body)

    if request.method == 'POST':                #先決是要有key (POST,GET)
        print ("POST: ")
        #print (body['id'])
        j_data = json.loads(json.dumps(body))  #str to dict to json
        print (j_data)
        #print ("{}".format(j_data))
        #print (json.dumps(body,ensure_ascii=False))

        '''
        print (request.values['id'])            #來自POST的header中parameter中的key:value
        print (request.values['name'])          #來自POST的header中parameter中的key:value
        print (request.values['done'])          #來自POST的header中parameter中的key:value

        print (request.form.to_dict())          #{'done': u'0', 'id': u'7', 'name': u'LLL'}

        print (list(request.form.keys()))       #來自POST的body中的key(全部list)
        print (request.form.get('id'))          #來自POST的body中的key:value
        print (request.form.get('name'))        #來自POST的body中的key:value
        print (request.form.get('done'))        #來自POST的body中的key:value
        '''
        task = {
        "id": nameing[-1]['id'] + 1,
        "name": j_data['name'],   #根據Client request {"name": "xxxx"}
        "done": True if 'True' in j_data['done'] else False
        }
    else:   #Because of "GET", that may have request "GET" value
        print ("GET: ")
        print (request.args.get('id'))           #來自GET的header中parameter中的key:value
        print (request.args.get('name'))           #來自GET的header中parameter中的key:value
        print (request.args.get('done'))           #來自GET的header中parameter中的key:value
        task = {
        "id": nameing[-1]['id'] + 1,
        "name": request.values['name'],   #根據Client request {"name": "xxxx"}
        "done": True if 'True' in request.values['done'] else False
        }

    nameing.append(task)
    return jsonify(nameing)    
    #[{"id":1,"name":"CHIPS"},{"id":2,"name":"garden"},{"id":3,"name":"L"}]

    #return jsonify({'nameing': nameing})    
    #{"nameing":[{"id":1,"name":"CHIPS"},{"id":2,"name":"garden"},{"id":3,"name":"L"}]}
