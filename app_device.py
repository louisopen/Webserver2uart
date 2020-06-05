#!/usr/bin/env python
#coding= utf-8

from ConsoleThreading import *
from flask import Flask, render_template, Response, request, redirect

Model='Web2uart Control'
app = Flask(__name__)

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