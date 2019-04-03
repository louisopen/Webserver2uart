import time  
import websocket  
import datetime  
import sys  
sys.path.append('/home/pi/rpi/code/Package')  
import grovepi  
from grove_rgb_lcd import *

sensor = 4  
blue = 0    # The Blue colored sensor.  
white = 1   # The White colored sensor.

websocket.enableTrace(True)  
ws = websocket.create_connection("ws://wot.city/object/57cad2809453b2446f0007de/send")

while True:  
    [temp,humidity] = grovepi.dht(sensor,blue)  
    print("temp = %.02f C humidity =%.02f%%"%(temp, humidity))
    setText("temp = %.02f C \nhumidity =%.02f%%"%(temp, humidity))
    t = time.time();
    date = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d%H%M%S')
    vals = "{\"date\":\""+date+"\",\"temperature\":"+str(temp)+",\"h\":"+str(humidity)+"}"
    time.sleep(1);
    ws.send(vals);
    print vals