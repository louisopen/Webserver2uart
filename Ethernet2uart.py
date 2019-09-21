#!/usr/bin/env python3
#coding=utf-8
"""
Subject: RS-485 via UART interface to Ethernet on Python
Interface: Master ethernet(Socket) with UART use simple http server for the setting
Description: Master data go with Socket to UART, then UART data go back to Socket(Master)
Aauther: louisopen@gmail.com
www: louisopen.github.io
"""
import sys
import serial
import socket
import time
#import RPI.GPIO as GPIO    #Raspberry pi GPIO
from random import *

sys.stderr = open("logstderr.txt", "w")     #turn to file log
print('Start the Python', file=sys.stderr)
print('Start the Python')

config = open("config.txt", "r")
if not config:
    #ModbusServer = "modbus.lewei50.com"
    ModbusServer = "www.electronicwings.com"
    ModbusPort = 9970
    userKey = 'your_userkey_in_Azure'

    ser=None
    serial_port="/dev/ttyUSB0"     #means serial of Linux
    #serial_port = 8    #means serial id 9 in windows
    #serial_port=0  
    serial_timeout=1
    serial_baud = 9600
    serial_EN_485 =  4
    print('total lines is system initial', file=sys.stderr, flush=True)
else:
    lines = config.readlines()
    for line in lines :
        part = line.strip().split("=")
        #print('lines is %s part is: %s' % lines)
        for index in enumerate(part):
            part[0] = part[0].strip(" ")
            if part[0] == 'ModbusServer': print(part[1].strip(" "))
            if part[0] == 'ModbusPort': print(part[1].strip(" "))
            if part[0] == 'userKey': print(part[1].strip(" "))
            if part[0] == 'ser': print(part[1].strip(" "))
            if part[0] == 'serial_port': print(part[1].strip(" "))
            if part[0] == 'serial_timeout': print(part[1].strip(" "))
            if part[0] == 'serial_baud': print(part[1].strip(" "))
            if part[0] == 'serial_EN_485': print(part[1].strip(" "))
            part[0]=''
    print('total lines is %s' % lines, file=sys.stderr, flush=True)
config.close()


def run(svr_status):

    global ser,serial_timeout,serial_port,serial_baud  

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ModbusServer, ModbusPort)
    #print >>sys.stderr, 'connecting to %s port %s' % server_address
    #print serial_port
    print('connecting to %s port %s' % server_address, file=sys.stderr)
    print('connect serial port %s' % serial_port, file=sys.stderr)
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
                print('fail to open serial port.', file=sys.stderr)
                ser.close()
                ser=None


            # Send data
            sock.connect(server_address)
            print('sending "%s"' % userKey, file=sys.stderr)
            sock.sendall(userKey)

            while 1:
                data = sock.recv(1024)
                print('received "%s"' % data, file=sys.stderr)
                '''try to send to serial'''
                try:
                    #GPIO.output(serial_EN_485,GPIO.HIGH)
                    ser.write(data)
                    #wait 1 second to get feed back from serial
                    time.sleep(1)
                    #GPIO.output(serial_EN_485,GPIO.LOW)
                    '''read from serial'''
                    n = ser.inWaiting()
                    print(n)

                    if(n>4):
                        serialData = ser.read(n)
                        sock.sendall(serialData)
                
                except:
                    print('error write to serial', file=sys.stderr)

                if data == "":
                    sock.close()
                    print('connection break! wait a while to reconnect')
                    time.sleep(10 + randint(1, 60))
                    run(0)
                    break
        finally:
            print('closing socket', file=sys.stderr)
            print('error write to serial', file=sys.stderr)         
            sock.close()
    except:
        print('fail')


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(serial_EN_485,GPIO.OUT)
    GPIO.output(serial_EN_485,GPIO.LOW) #RS-485 enable control.
    run(0)