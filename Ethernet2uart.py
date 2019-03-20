#!/usr/bin/env python
# -*- coding: utf_8 -*-

"""
 RS-485 via UART interface for python
 auther louisopen@gmail.com
"""

import sys
import serial
import socket
import time
import RPi.GPIO as GPIO
from random import *

#ModbusServer = "modbus.lewei50.com"
ModbusServer = "www.electronicwings.com"
ModbusPort = 9970
userKey = 'your_userkey_in_Azure'


ser=None
#serial_port="/dev/ttyUSB0"
serial_port=0    #serial_port = 8  means serial id 9 in windows
serial_timeout=1
serial_baud = 9600
serial_EN_485 =  4


def run(svr_status):

    global ser,serial_timeout,serial_port,serial_baud  

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ModbusServer, ModbusPort)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    #print serial_port
    #sock.bind(server_address)
    #sock.listen(1)
    #print >>sys.stderr, 'waiting for a connection ' connection, client_address = sock.accept()

    try:

        try:

            try:

                if ser is None:
                    ser=serial.Serial(port=serial_port, baudrate=serial_baud, bytesize=8, parity="N", stopbits=1, xonxoff=0)
                    #ser.setTimeout(serial_timeout)

            except:

                print "fail to connect serial"
                ser.close()
                ser=None

            # Send data
            sock.connect(server_address)
            print >>sys.stderr, 'sending "%s"' % userKey
            sock.sendall(userKey)

            while 1:
                data = sock.recv(1024)
                print >>sys.stderr, 'received "%s"' % data

                '''try to send to serial'''
                try:
                    #GPIO.output(serial_EN_485,GPIO.HIGH)
                    ser.write(data)
                    #wait 1 second to get feed back from serial
                    time.sleep(1)

                    '''read from serial'''
                    n = ser.inWaiting()
                    #GPIO.output(serial_EN_485,GPIO.LOW)
                    print(n)

                    if(n>4):
                        serialData = ser.read(n)
                        sock.sendall(serialData)
                

                except:
                    print "error write to serial"

                if data == "":
                    sock.close()
                    print "connection break!wait a while to reconnect"
                    time.sleep(10 + randint(1, 60))
                    run(0)
                    break

        finally:
            print >>sys.stderr, 'closing socket'
            sock.close()

    except:
        print "fail"

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(serial_EN_485,GPIO.OUT)
    GPIO.output(serial_EN_485,GPIO.LOW) #RS-485 enable control.
    run(0)