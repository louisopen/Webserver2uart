#!/usr/bin/env python
#coding= utf-8

import serial
import serial.tools.list_ports
from threading import Thread
import time, os, sys, datetime
#===========================================================================
class SerialTask:
	def __init__(self, p_ch, baud):
		self._running = False	#True is for Slave mode waitting RXD command
		self.getData=''
		self.rec_string=''
		self.debounce=0
		self.p_ch=p_ch
		#find all available devices
		ports  = list(serial.tools.list_ports.comports())
		#Open the port
		for self.p in ports:
			print '\rSerial port is detected %s'%self.p		
			#/dev/ttyUSB1 - 5491B Multimeter
			#/dev/ttyUSB0 - FT232R USB UART
			#/dev/ttyAMA0 - ttyAMA0
			if self.p_ch in self.p:
				print '\rConnect to Serial port %s'%self.p
				try:
					#print '\rRaspberry is detected %s'%p[0]
					self.serial_port = serial.Serial(port=self.p[0], baudrate=baud, timeout=1, writeTimeout=1)
					if not self.serial_port.isOpen():
						self.serial_port.open()
					self._running = True
					break
				#except:
				except (OSError, serial.SerialException):
					print ("\rUnexpected error:", sys.exc_info())
					pass
	def isopen(self):
		#print self.p[0]
		if self.p_ch==self.p[0]:
			return True
		return False		
		#if self._running:
		#	return True
		#return False
	def isOpen(self):
		#if not self.serial_port.isOpen():
		#	if self.serial_port.open():
		#		return True
		#return False
		if self._running:
			return True
		return False
	def read(self,num):
		return self.serial_port.read(num)
	def readline(self):
		return self.serial_port.readline()
	def terminate(self):
		self._running = False
		self.serial_port.close()
	#def write(self,data):		#write anything		
		#self.serial_port.write(data.encode('utf-8'))
	def send(self,data):		#write anything
		if not data:
			return
		#self.serial_port.flushInput()
		#self.serial_port.flushOutput()
		#serial_port.write('\r'.encode('utf-8'))
		self.serial_port.write(data.encode('utf-8'))
		#self.serial_port.write(data.decode("hex"))
		time.sleep(0.2)
	def receive(self):			#read anything
		#return bytes.decode(self.serial_port.read(256))
		time_out=0
		while self.rec_string=='':
			time.sleep(0.01)
			time_out+=1
			if time_out>150:	#set time out 1.5sec.
				return ''
			pass
		temp=self.rec_string
		self.rec_string=''
		return temp
	def function_status(self):
		comm=':func?\r'
		self.serial_port.write(comm.encode('utf-8'))
		#self.getData=bytes.decode(self.serial_port.read(256))	#get function string
		#time.sleep(0.3)
		self.getData=self.receive()	#get function string
		return self.getData
	def function_read(self):		
		comm=':fetch?\r'
		self.serial_port.write(comm.encode('utf-8'))
		#self.serial_port.flushInput()
		temp=0
		try:
			#cmds=bytes.decode(self.serial_port.read(256)).split()
			cmds=self.receive().split()
			#print '\r%s %s'%(len(cmds), cmds)		#debug
			temp=float(cmds[1])
		except:
			pass
		#time.sleep(0.4)
		return temp
	def current_dc_range(self,range):
		comm=':func curr:dc ;:curr:dc:rang '+range+'\r'	#-20~20
		self.serial_port.write(comm.encode('utf-8'))
		time.sleep(0.4)
		return self.function_status()
	def voltage_dc_range(self,range):
		comm=':func volt:dc ;:volt:dc:rang '+range+'\r'	#-0.2~1000
		self.serial_port.write(comm.encode('utf-8'))
		time.sleep(0.4)
		return self.function_status()
	def frequency_range(self,range):
		comm=':func freq ;:freq:thr:volt:rang '+range+' ;:freq:ref 100000\r'	#volt(0~1010)  ref(2000000)
		self.serial_port.write(comm.encode('utf-8'))
		#self.serial_port.flushInput()
		#self.serial_port.flushOutput()
		time.sleep(0.8)
		return self.function_status()
	def resistance_range(self,range):
		comm=':func res ;:res:rang '+range+'\r'	#nplc(0.1~10) rang(0~20000000)
		#comm=':func res ;:res:nplc 1 ;:res:rang '+range+'\r'	#nplc(0.1~10) rang(0~20000000)
		self.serial_port.write(comm.encode('utf-8'))
		#self.serial_port.flushInput()
		time.sleep(0.8)
		return self.function_status()
	def run(self,message):
		#self.serial_port.write('\r\nStart '+ Model +' Serial\r\nshell>'.encode('utf-8'))
		self.serial_port.flushInput()
		while self._running:
			try:
				#ch = bytes.decode(serial_port.read(1))
				ch = self.serial_port.read(1)
				if ch =='':
					#print '\r\nTime: %s'%datetime.datetime.now().strftime('%H:%M:%S')
					self.debounce += 1
					if self.debounce > 2:		#2 sec. if timebase is 0.125
						#print '\r\nClear: %s'%self.getData
						self.getData=''
						self.debounce=0
					pass
				elif ch == '\n':	##############Normally for 0D0A##################
				#elif ch == '\x0a':	##############Special for 5491B##################
					if self.getData !='':
						#process_receive(self.getData)		#here for app_ipad & normal devices
						self.rec_string=self.getData		#or here for app_ipad & normal devices
						pass
					#print '\r\nEnter: %s'%self.getData		#DEBUG
					self.getData=''
					self.debounce=0
				##############Special for 5491B##################
				#elif ch == '\x0d':		#elif ch == '\r': 	#丟棄返回的指令(if BK5491B)
				#	#print '\r\nFeed: %s'%self.getData		#DEBUG
				#	self.getData=''
				#	self.debounce=0
				else:
					#print '\r\nCh: %s'%ch
					#ch = ch.upper()
					self.getData += bytes.decode(ch)
					self.debounce=0
					#print '\r\nString: %s'%self.getData	#DEBUG
					time.sleep(0.005)
					continue
			except Exception, e:
				print '\r\nSerial port: %s\r\nshell>'% str(e)
				self.getData=''
				pass
			time.sleep(0.125)
		#GPIO.output(LED[1],GPIO.LOW)
#===========================================================================
def process_receive(getData):	#for Master
	#cmds=[for x in input().split()]
	#cmds=[getData.split()]	
	#cmds=[getData.split('',2)]
	#cmds=getData.split()
	cmds=getData.split(':')
	print '\r\nCommand: %s %s'%(len(cmds), cmds)	#Change 20200413
	try:
		#watchdog = Watchdog(4, restart_program)  	#使用自己的Handler(),否則就使用類庫內定義handler
		if cmds[0]=='volt':
			#logmsg=cmds[1]
			pass
		elif cmds[0]=='curr':
			#logmsg=cmds[1]
			pass
		else:
			print '\r\nCommand: %s'%cmds[0]
			pass
	except:
		pass
	#watchdog.stop()
	return cmds
"""	return {
	'a': 1,
		print '1'
	'b': 2,
		print '2'
	'c': 3,
		print '3'
	}
	}.get(var,'error')  #'error'為預設返回值，可自設定
"""
#===========================================================================
#Call example
#===========================================================================
def app1(Serial):
	if Serial.isOpen():
		Serial.send('*IDN?\r')
		print '\r%s'%Serial.receive()
		
		print '\r%s'%Serial.frequency_range('500')
		print '\r%s\n'%Serial.function_read()
		#print '\r%s'%Serial.receive()

		print '\r%s'%Serial.resistance_range('200000')
		print '\r%s\n'%Serial.function_read()
		#print '\r%s'%Serial.receive()
		
		for i in range (1,50,1):
			print '\r\nSwitch to curr:'
			message=":func curr:dc ;:curr:dc:rang 0.5\r"
			Serial.send(message)
			#message=":func?\r"			#':func?\r' request mode, ":func\r" just for beep echo
			#Serial.send(message)
			print '\r%s'%Serial.receive()
			
			message=':fetch?\r'
			Serial.send(message)
			print '\r%s\n'%Serial.receive()
			print '\r%s\n\n'%Serial.function_status()
			time.sleep(0.5)
			################################################################
			print '\r\nSwitch to volt:'
			message=":func volt:dc ;:volt:dc:rang 5\r"
			Serial.send(message)
			#message=":func?\r"			#':func?\r' request mode, ":func\r" just for beep echo
			#Serial.send(message)
			print '\r%s'%Serial.receive()

			message=':fetch?\r'
			Serial.send(message)
			print '\r%s\n'%Serial.receive()
			print '\r%s\n\n'%Serial.function_status()
			time.sleep(0.5)
#===========================================================================
def app2(Serial):
	if Serial.isOpen():
		Serial.send('*IDN?\r')
		#print '\r%s\n'%Serial.function_read()
		print '\r%s'%Serial.receive()
		'''
		print '\r%s'%Serial.frequency_range('500')
		print '\r%s\n'%Serial.function_read()
		#print '\r%s'%Serial.receive()

		print '\r%s'%Serial.resistance_range('200000')
		print '\r%s\n'%Serial.function_read()
		#print '\r%s'%Serial.receive()
		'''
		#==================================================================#		
		for i in range (1,100,1):
			print '\r%s'%Serial.current_dc_range('0.5')
			print '\r%s\n'%Serial.function_read()
			#print '\r%f\n'%(Serial.function_read()*10000000)
			
			print '\r%s'%Serial.voltage_dc_range('5')
			print '\r%s\n'%Serial.function_read()
			#print '\r%f\n'%(Serial.function_read()*10000000)

			print '\r%s'%Serial.frequency_range('500')
			print '\r%s\n'%Serial.function_read()
			#time.sleep(0.5)
			#print '\r%s'%Serial.resistance_range('50000000')
			time.sleep(0.5)
			print '\r%s\n'%Serial.function_read()
#===========================================================================
def appBK(Serial):	#for test write only
	if Serial.isOpen():		
		Serial.send('*IDN?\r')	
		for i in range (1,100,1):
			Serial.send(':func?\r')
			time.sleep(0.5)
#===========================================================================
def app_PSW(Serial):
	if Serial.isOpen():
		message='*IDN?\n'
		Serial.send(message)
		time.sleep(0.1)
		print '\r%s'%Serial.receive()

		for i in range (1,50,1):
			message='SOUR:VOLT:LEV:IMM:AMPL 5.2\n'
			Serial.send(message)
			message='SOUR:CURR:LEV:IMM:AMPL 1.0\n'
			Serial.send(message)
			message='OUTP:DEL:ON 0.5\n'
			Serial.send(message)
			message='OUTP:STAT:IMM ON\n'
			Serial.send(message)

			time.sleep(0.5)
			#message='STAT:QUES:COND?\n'
			#message='OUTP:MODE?\n'
			#message='OUTP:STAT:IMM?\n'
			#message='MEAS:SCAL:CURR:DC?\n'
			message='MEAS:SCAL:VOLT:DC?\n'
			Serial.send(message)
			time.sleep(0.1)
			print '\r%s'%Serial.receive()
#===========================================================================
def app_ipad(Serial):
	if Serial.isOpen():
		message='*IDN?\r'
		Serial.send(message)
		time.sleep(0.1)
		print '\r%s'%Serial.receive()
		message='model\r'
		Serial.send(message)
		time.sleep(0.1)
		print '\r%s'%Serial.receive()
		for i in range (1,100,1):
			message='STBY\r'
			Serial.send(message)
			time.sleep(0.1)
			print '\r%s'%Serial.receive()
			pass
#===========================================================================
if __name__=='__main__':
	#Serial = SerialTask('/dev/ttyAMA0',115200)	#test Slave of the PC station control
	#Serial = SerialTask('/dev/ttyUSB0',115200)	#test Master of ipad myself
	#Serial = SerialTask('/dev/ttyUSB0',9600)	#test Master of BK5491B
	Serial = SerialTask('/dev/ttyACM0',115200)	#test Master of PSW 80-13.5 power supply
	if Serial.isopen():	
		task = Thread(target=Serial.run, args=('for_serial_class',))	#開啟Allocate threading function
		task.start()	#啟動
		try:
			#app1(Serial)		#BK5491B
			#app2(Serial)		#BK5491B
			#appBK(Serial)		#BK5491B
			app_PSW(Serial)	#PSW 80-13.5 Power supply
			#app_ipad(Serial)	#X1608...
		except KeyboardInterrupt:
			pass
		Serial.terminate()
		task.join()