# Project code- Lab 2
# Author- Abhishek
# Uta Id- 1001773413

# https://github.com/effiongcharles/multi_user_chat_application_in_python/blob/master/client_gui.py
import Tkinter as tk
import tkMessageBox as messagebox
import tkSimpleDialog as simpleDialog
from os import listdir
from distutils.dir_util import copy_tree
import threading
import socket
import shutil 
import re
import os
import sys
import time
# mode 
mode = 0o666
parent_dir = './LD'

# UI for clinet using tKinter
window = tk.Tk()
window.title("Client")
username = " "

topFrame = tk.Frame(window)
lblName = tk.Label(topFrame, text = "Name:").pack(side=tk.LEFT)
entName = tk.Entry(topFrame)
entName.pack(side=tk.LEFT)
btnConnect = tk.Button(topFrame, text="Connect", command=lambda : connect())
btnConnect.pack(side=tk.LEFT)
#btnConnect.bind('<Button-1>', connect)
topFrame.pack(side=tk.TOP)

displayFrame = tk.Frame(window)
lblLine = tk.Label(displayFrame, text="*********************************************************************").pack()
configTxt = tk.Label(displayFrame, text = "Unknown Identifier")
configTxt.pack()
scrollBar = tk.Scrollbar(displayFrame)

scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP)


bottomFrame = tk.Frame(window)
tkMessage = tk.Text(bottomFrame, height=2, width=55)
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind("<Return>", (lambda event: getChatMessage(tkMessage.get("1.0", tk.END))))
bottomFrame.pack(side=tk.BOTTOM)

# code to connect to server
def connect():
    global username, client
    # https://stackoverflow.com/questions/25063248/regex-to-not-allow-string-start-or-end-with-special-character-and-should-not-hav
    username = entName.get()
    regex = re.compile("^(?!.*[-_]{2})(?=.*[a-z0-9]$)[a-z0-9][a-z0-9_-]*$")
    if (regex.search(username) == None):
        messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name <e.g. Ram>")
    else:
      
        connect_to_server(username)


# network client
client = None
HOST_ADDR = "0.0.0.0"
HOST_PORT = 8080

def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name) # Send name to server after connecting

        entName.config(state=tk.DISABLED)
        btnConnect.config(state=tk.DISABLED)
        tkMessage.config(state=tk.NORMAL)

        # start a thread to keep receiving message from server
        # do not block the main thread :)
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")


# https://www.geeksforgeeks.org/find-length-of-a-string-in-python-4-ways/
dirName = './server_directory'
def getListOfFiles(dirName):
    allFiles = list()
    os.walk(dirName)   
    allFiles= [x[0] for x in os.walk(dirName)] 
    allFiles.pop(0)
    y = []
    for i in allFiles:
        result = i.find('home_directory') 
        y.append(i[result:])   
    return y

identifier = []
flag1 = False 
# Function to receive msg from server and creating identifers for users
def receive_message_from_server(sck, m):
    while True:
        from_server = sck.recv(4096)
        if not from_server: break

        # display message from server on the chat window

        # enable the display area and insert the text and then disable.
        # why? Apparently, tkinter does not allow us insert into a disabled Text widget :(
        texts = tkDisplay.get("1.0", tk.END).strip()
        tkDisplay.config(state=tk.NORMAL)
        if (from_server.find('exists') != -1):
            print("clear the field and disabled the lower i/p")
            # entName = ""
            tkDisplay.insert(tk.END, from_server)
            entName.config(state=tk.NORMAL)
            btnConnect.config(state=tk.NORMAL)

        elif (from_server.find('Welcome') != -1):
            response = from_server.split()
            # from_server ="Indentifier A"
            id1 = response[5][5]
            identifier.append(response[0])
            print(id1)
            list1 = getListOfFiles(dirName)
            if id1=='1':
                flag1 = True
                configTxt.config(text="Indentifier A")
                configTxt.pack()
                path = os.path.join(parent_dir, "A")
                os.mkdir(path)
            #    Write code to remove the num in the string
                from_server = from_server[0:len(from_server)-1]
                tkDisplay.insert(tk.END, "\n\n"+ from_server)
                
                # tkDisplay.insert(tk.END, "\n\n"+ 'List of directories on server')
                tkDisplay.insert(tk.END, "\n\nList of directories on server:-"+ str(list1))
                tkDisplay.insert(tk.END, "\n\nEnter 'sync 1-->to sync home_directory_1'")
                print(list1)
                # show the list of directories in tkinter
            elif id1 == '2':
                configTxt.config(text="Indentifier B")
                configTxt.pack()
                path = os.path.join(parent_dir, "B")
                os.mkdir(path)
                tkDisplay.insert(tk.END, "\n\n"+ from_server)
                tkDisplay.insert(tk.END, "\n\nList of directories on server:-"+ str(list1))
                tkDisplay.insert(tk.END, "\n\nEnter 'sync 1-->to sync home_directory_1'")

            elif id1 == '3':
                configTxt.config(text="Indentifier C")
                configTxt.pack()
                path = os.path.join(parent_dir, "C")
                os.mkdir(path)
                tkDisplay.insert(tk.END, "\n\n"+ from_server)
                tkDisplay.insert(tk.END, "\n\nList of directories on server:-"+ str(list1))
                tkDisplay.insert(tk.END, "\n\nEnter 'sync 1-->to sync home_directory_1'")
            else:
                print("not a valid output")
            # print(response) 
            # snippet to sync directories 
        elif(from_server.find('sync') != -1):
            temp = from_server.split()
            print(temp)
            if(len(temp)>2):
                if(temp[2]=='0'):
                    dirName1 = './LD/'+'A'
                if(temp[2]=='1'):
                    dirName1 = './LD/'+'B'
                if(temp[2]=='2'):
                    dirName1 = './LD/'+'C' 

                if(temp[1]=='1'):
                    print('sync home1')
                    tkDisplay.insert(tk.END, "\n\nEnter 'copied home_directory_1'")
                    src = './server_directory/home_directory_1'
                    print(dirName1)
                    path = os.path.join(dirName1, "home_directory_1")
                    os.mkdir(path)

                    copy_tree(src, path)
                    # destination = shutil.copytree(src, dirName1)
                if(temp[1]=='2'):
                    print("sync home2")
                    src = './server_directory/home_directory_2'
                    path = os.path.join(dirName1, "home_directory_2")
                    os.mkdir(path)

                    copy_tree(src, path)
                    tkDisplay.insert(tk.END, "\n\nEnter 'copied home_directory_2'")
                if(temp[1]=='3'):
                    print("sync home3") 
                    src = './server_directory/home_directory_3'
                    path = os.path.join(dirName1, "home_directory_3")
                    os.mkdir(path)
                    copy_tree(src, path)
                    tkDisplay.insert(tk.END, "\n\nEnter 'copied home_directory_3'")

# code snippet to update the local LD dir
        elif(from_server.find('Update') != -1):
            listOfLD = os.listdir('./LD')
            listOfLD.pop(0)
            print(listOfLD)
            for i in listOfLD:
                if i == 'A':
                    funct_A('A')
                if i == 'B':
                    funct_A('B')
                if i == 'C':
                    funct_A('C')        

           
        else:

            print(texts)
            if len(texts) < 1:
                print("in if")
                tkDisplay.insert(tk.END, from_server)
            else:
                print("in else")
                tkDisplay.insert(tk.END, "\n\n"+ from_server)

            # entName.config(state=tk.DISABLED)
            # btnConnect.config(state=tk.DISABLED)
            tkDisplay.config(state=tk.DISABLED)
            tkDisplay.see(tk.END)
       
        print("Server says: " +from_server)

    sck.close()
    window.destroy()

def funct_A(item):
    dir_A = os.listdir('./LD/' + item)
    for i in dir_A:
        if not item.startswith('.'):
            path = os.path.join('./LD/' + item +  '/'+i) 
            if os.listdir(path):
                print(os.listdir(path))
                shutil.rmtree(path) 
                src = dirName + '/' + i
            path = os.path.join('./LD/'+item,i)
            os.mkdir(path)
            copy_tree(src,path)

# Function to receive text msg from chat messenger
def getChatMessage(msg):
    print("this function was also")
    print("msg +="+msg)

    msg = msg.replace('\n', '')
    texts = tkDisplay.get("1.0", tk.END).strip()

    # enable the display area and insert the text and then disable.
    # why? Apparently, tkinter does not allow use insert into a disabled Text widget :(
    tkDisplay.config(state=tk.NORMAL)
    if len(texts) < 1:
        tkDisplay.insert(tk.END, "You->" + msg, "tag_your_message") # no line
    else:
        tkDisplay.insert(tk.END, "\n\n" + "You->" + msg, "tag_your_message")

    tkDisplay.config(state=tk.DISABLED)

    send_mssage_to_server(msg)

    tkDisplay.see(tk.END)
    tkMessage.delete('1.0', tk.END)

# Function to send text to server
def send_mssage_to_server(msg):
    client.send(msg)
    print(msg)
    if msg == "exit":
        client.close()
        window.destroy()
        # destination = shutil.copytree(src, dest)
    print("Sending message")
    print(flag1)

window.mainloop()


   