# Project code- Lab 2
# Author- Abhishek
# Uta Id- 1001773413

# https://github.com/effiongcharles/multi_user_chat_application_in_python/blob/master/server_gui.py
import Tkinter as tk
import socket
import threading
import os
import sys
import shutil
import time
import os.path

# mode 
mode = 0o666
parent_dir = './directories'
server_dirs = './server_directory/'
window = tk.Tk()
window.title("Server")

# Top frame consisting of two buttons widgets (i.e. btnStart, btnStop)
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Connect", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)   
topFrame.pack(side=tk.TOP, pady=(5, 0))

# Middle frame consisting of two labels for displaying the host and port info
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Host: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# The client frame shows the client area
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="**********Client List**********").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=15, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None
HOST_ADDR = "0.0.0.0"
HOST_PORT = 8080
client_name = " "
clients = []
clients_names = []
arr_list = []

# Start server function
def start_server():
    global server, HOST_ADDR, HOST_PORT # code is fine without this
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print socket.AF_INET
    print socket.SOCK_STREAM

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # server is listening for client connection

    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Host: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)


# Stop server function
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)

# Function to accept the clients 
def accept_clients(the_server, y):
    while True:
        client, addr = the_server.accept()
        clients.append(client)

        # use a thread so as not to clog the gui thread
        threading._start_new_thread(send_receive_client_message, (client, addr))
        threading._start_new_thread(changesInDirectory, ())



# Function to get the actual length of files in directories
def rest_dir_length():
    global set_len
    listOfDirectories = os.listdir('./server_directory')
    file_len = 0
    for directory in listOfDirectories:
        for root, dirs, files in os.walk(server_dirs + str(directory)):
            file_len += len(files)   
   
    set_len = file_len
    print('set len= '+ str(set_len))
    # return file_len

rest_dir_length()

# Function to get the updated length
def dir_length():
    # simple version for working with CWD
    listOfDirectories = os.listdir('./server_directory')
    # print(server_dirs+listOfDirectories[0])
    file_len1 = 0
    for directory in listOfDirectories:
        for root, dirs, files in os.walk(server_dirs + str(directory)):
            file_len1 += len(files)   
    return file_len1

# Function to detect the change in directories
def changesInDirectory():
    threading.Timer(2.0, changesInDirectory).start()
    latest_dir_len = dir_length()
    print(latest_dir_len, set_len)
    # set_dir_len = rest_dir_length()
    if cmp(latest_dir_len, set_len) == 0:
        print('not updated')
    else:
        print('dir updated')
        update_dir()
        rest_dir_length()
        
# Function to update the users for changes in the directories
def update_dir():
    for client in clients:
        client.send("Update dirs")

# Function to receive message from current client AND removing client from server if client closes
# Send that message to other clients
flag = True
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, clients_addr
    client_msg = " "
    # send welcome message to client
    client_name  = client_connection.recv(4096)

    if clients_names:
        for name in clients_names:
            if name == client_name:
                 client_connection.send("Username already exists. Use 'exit' to quit")
                 flag = True
                 break
            else:
                flag = False

    if len(clients_names)== 0 or flag == False:
        # client_connection.send("Welcome " + client_name + ". Use 'exit' to quit")
        clients_names.append(client_name)
        path = os.path.join(parent_dir, client_name)
        os.mkdir(path)
        update_client_names_display(clients_names)  # update client names display
        print("user_len="+str(len(clients_names)))
        client_connection.send("Welcome " + client_name + ". Use 'exit' to quit!" + str(len(clients_names)))


    while True:


        data = client_connection.recv(4096)
        if not data: break
        if data == "exit": break

        client_msg = data
        # print("Hello world!")
        # print(client_msg)
        idx = get_client_index(clients, client_connection)
        client_name = clients_names[idx]
        print('name='+client_name)
        print(clients_names)
        # print(client_connection.recv(4096))
        val = dir_cmd(client_msg, path, idx)
        print('val='+val)
        client_connection.send(val)    


    # find the client index then remove from both lists(client name list and connection list)
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    client_connection.send("BYE!")
    client_connection.close()

   
    
    update_client_names_display(clients_names)  # update client names display

# Return the index of the current client in the list of clients
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


# Update client name display when a new client connects OR
# When a connected client disconnects

def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c+"\n")
    tkDisplay.config(state=tk.DISABLED)
    arr_list = str(len(name_list))
    print("name_list="+arr_list)
    # return arr_list)


# Function to write all directory commands
def dir_cmd(msg, name, id1):
    x = ''
    print("msg, name")
    print(msg)
    print(name)
    temp = msg.split()
    # print(temp)
    flag = False
    # code snippet to make directory
    if temp[0] == "mkdir":
        path = os.path.join(name, temp[1])
        os.mkdir(path)
        x = "Directory made successfully."
        flag = True
    # code snippet to delete directory
    if temp[0] == "rm":
        print("delete directory")
        if(os.name):
            # Path  
            path = os.path.join(name, temp[1]) 
            os.rmdir(path) 
            f_list = []
            x = "deleted the directory"
            flag = True
    # code snippet to rename a directory
    if temp[0] == "rn":
        os.rename(name + "/" +temp[1], name + "/" + temp[2])
        x = "Directory renamed successfully"
        flag = True

    # code snippet to list the elements in a directory
    if temp[0] == 'ls':
       f_list = []
       for f in os.listdir(name): 
            # if os.name.isfile(os.name.join(name, f)): 
            f_list.append(f) 
            print(f_list)
       x = ' '.join(f_list)
       flag = True

     # code snippet to move the directory
    if temp[0] == 'mv':
        new_path = shutil.move(name + "/" + temp[1], name + "/"+temp[2]) # move the file to the destination directory
        print('File moved to: ' + str(new_path)) # indicate success
        flag = True
        x = "File moved successfully"
    if temp[0] == 'sync':
        x = msg + ' ' +str(id1)
        flag = True
    if(flag==False):
        x= "illegal command"
    return x
    f_list = []
window.mainloop()

