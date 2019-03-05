import socket 
host = '' 
port = 4001 
backlog = 5 
size = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind((host,port)) 
s.listen(backlog) 
while 1: 
    client, address = s.accept() 
    data = client.recv(size) 
    if data: 
        print(data)
    client.close()



import serial
ser = serial.serial_for_url("socket://localhost:4001/logging=debug")
data = ser.read(8)
if data:
    print(data)
    ser.flushOutput()
ser.close()
