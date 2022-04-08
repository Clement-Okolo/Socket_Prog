# -*- coding: utf-8 -*-

import socket
import sys
import collections
import time
import queue
import threading

from threading import Thread
from socketserver import ThreadingMixIn

lock = threading.Lock()
global command
command = ""

sendqueues = {}
TCP_IP = "127.0.0.1"
TCP_PORT = 3000
TCP_PORT2 = 125
BUFFER_SIZE = 20  # Normally 1024, but we want fast response
TIME_OUT = 1800.0 #seconds   - For time_out    Block_time is 60 seconds
BLOCK_TIME = 60.0


curusers = []
offlineusers = []
blockusers = []
userlog = {}
userfdmap = []


tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#host = socket.gethostname()
tcpsock.bind(("127.0.0.1", TCP_PORT))

tcpsock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock2.bind(("127.0.0.1", TCP_PORT2))

class ClientThread(Thread):

    def __init__(self,socket,ip,port):
        Thread.__init__(self)
        self.socket = socket
        self.ip = ip
        self.port = port
        print ("New thread started")



    def run(self):

        status = 0
        userpresent = 0
        while True:
            self.socket.send(bytes(str(TIME_OUT),"utf8"))
            data2 = "successful"
            while userpresent == 0:
                num = 0
                userdata = self.socket.recv(2048).decode("utf8")


                if not userdata: break

                line = open('user_pass.txt').readlines()
                for userpass in line:
                    #print("entered userpass")
                    user = userpass.split(" ")
                    if userdata == user[0]:
                        userpresent = 1
                if userpresent == 0:
                    #print("here it is 1")
                    data2 = "invalid login"
                    status = 0
                    #print(data2)
                    #print("here it is 2")
                    #data2 = bytes("invalid login",'utf8')
				    #data2 = bytes(" invalid login ",'utf8')
                    #print("sending invalid login 2 from server")
                    self.socket.send(bytes(data2,"utf8"))

                    continue
                else:
                    #print("in blockusers")
                    for p in blockusers:
                        print ("blockusers: " , p)
                        val = p.partition(" ")
                        valin = val[2].partition(" ")
                        curtime =time.time()
                        if val[0] == userdata and float(valin[0]) >= curtime - BLOCK_TIME and valin[2] == str(ip):     #Blocktime and ip
                            data2 = " blocked "
                            status = 2

                    for p in curusers:
                        print ("curusers:", p)
                        if userdata == p:
                            data2 = "same user"
                            status = 1
                            print (data2)
                    if data2 == " blocked ":

                        #data2 = bytes(" blocked ",'utf8')
                        self.socket.send(bytes(data2,"utf8"))
                        status = 2
                    elif data2 == "same user":
                        #data2 = bytes("same user",'utf8')
                        self.socket.send(bytes(data2,"utf8"))
                        status = 1


            if data2 == "successful":
                #data2 = bytes("successful",'utf8')
                self.socket.send(bytes(data2,"utf8"))
                passpresent = 0
                while status == 0:
                    passdata = self.socket.recv(2048).decode("utf8")
                    validity = userdata + " " + passdata

                    if (validity not in open('user_pass.txt').read()):
                        data2 = "invalid password"
                        #data2 = bytes("invalid password",'utf8')
                        #print (data2)
                        num = num + 1
                        if num == 3:
                            status = 2
                            #data2 = bytes("invalid password",'utf8')
                            self.socket.send(bytes(data2,"utf8"))
                            print ("breaking")
                            break


                        else:
                            status = 0
                            self.socket.send(bytes(data2,"utf8"))

                    else:
                        data2 = "successful"
                        #data2 = bytes("successful",'utf8')
                        self.socket.send(bytes(data2,"utf8"))
                        for p in offlineusers:
                            t = p.partition(" ")
                            if t[0] == userdata:
                                lock.acquire()
                                offlineusers.remove(p)
                                lock.release()

                        lock.acquire()
                        curusers.append(userdata)
                        lock.release()
                        print (userdata + " logged in")
                        status = 1  # 0 for offline , 1 for online , 2 for blocked
                        logtime=time.time()
                        fd = self.socket.fileno()
                        userfd = userdata + " " + str(fd)
                        lock.acquire()
                        userfdmap.append(userfd)
                        lock.release()




           # print "[+] thread ready for "+ip+":"+str(port)
            if (status == 2 and num == 3):
                blockuserdata = userdata + " " + str(time.time()) + " " + str(ip)
                blockusers.append(blockuserdata)
                fd = self.socket.fileno()
                lock.acquire()
                del sendqueues[fd]
                lock.release()
                print (blockuserdata, " blocked for 60 seconds")
                sys.exit()


            else:

                while True:
                    self.socket.settimeout(TIME_OUT)
                    command = self.socket.recv(2048)
                    #print('printing from server')
                    #print(command)
                    #command = command.decode("utf-8")
                    #print('printing command from server')
                    #print(command)
                    if 'send '  in command.decode("utf8"):
                        #print("sending print from server")
                        print(userdata + " "+command.decode("utf8"))
                        content = command.partition(bytes(" ","utf8"))
                        contentinner = content[2].partition(bytes(" ","utf8"))
                        sendmsg = userdata + ": " + contentinner[2].decode("utf8")

                        receiver = contentinner[0]
                        errorflag = 1


                        for z in userfdmap:
                            zi = z.partition(" ")
                            if zi[0] == receiver:
                                receiverfd = int(zi[2])

                                errorflag = 0
                                lock.acquire()
                                sendqueues[receiverfd].put(sendmsg)
                                lock.release()



                        if errorflag == 1:
                            replymsg = "User is offline.  Don't worry , we will get it delivered."     #offline messaging
                            file = open('{0}.txt'.format(receiver),"a+")
                            localtime = time.asctime( time.localtime(time.time()) )
                            sendmsg = sendmsg + " " + "on" + " " + localtime
                            file.write(sendmsg)
                            file.write("\n")
                            file.close()

                        else:

                            replymsg = "message sent"

                        self.socket.send(bytes(replymsg,"utf8"))

                    elif "broadcast user" in command.decode("utf8"):
                        content = command.split(" ")
                        receivers = []
                        messageflag = 0
                        sendmessage = userdata + ":"
                        for i, val in enumerate(content):
                            if ( i != 0 or i != 1):
                                if val != "message" and messageflag == 0:
                                    receivers.append(val)
                                elif val == "message":
                                    i = i + 1
                                    messageflag = 1
                                elif messageflag == 1:
                                    sendmessage = sendmessage + " " + val





                        for p in receivers:
                            print (p)
                            errorflag = 1
                            for z in userfdmap:
                                zi = z.partition(" ")
                                if p == zi[0]:
                                    receiverfd = int(zi[2])
                                    print (receiverfd)
                                    errorflag = 0
                                    lock.acquire()
                                    sendqueues[receiverfd].put(sendmessage)
                                    lock.release()
                        if errorflag == 1:

                            replymsg = "Cannot broadcast message to all , few users offline"
                        else:
                            replymsg = "message broadcasted"
                            self.socket.send(replymsg)



                    elif command.decode("utf8") == "inbox":
                             print(userdata + " checked inbox")
                             sendmsg = ""
                             file = open('b\'{0}\'.txt'.format(userdata),"r")
                             file.seek(0)
                             first_char = file.read(1)
                             if not first_char:
                                 sendmsg = "Your Inbox is empty"
                             else:
                                 print("Inbox messages are as follows:")
                                 file.seek(0)
                                 for msg in file:
                                     sendmsg = sendmsg + "\n" + msg
                                     print(sendmsg)
                             self.socket.send(bytes(sendmsg,"utf8"))







                    elif command.decode("utf8") == "whoelse":
                        online = " "
                        print("Following members are online")
                        for p in curusers:

                            if p != userdata:
                                online = online + p + " "
                        self.socket.send(bytes(online,"utf8"))
                   

                        # self.socket.send(offline)
                    elif command.decode("utf8") == "logout":
                        print(userdata +"logged out")
                        curusers.remove(userdata)
                        offlinedata = userdata + " " + str(logtime)
                        lock.acquire()
                        offlineusers.append(offlinedata)
                        lock.release()
                        print (offlinedata , "removed")
                        logoutack = "logged out"
                        self.socket.send(bytes(logoutack,"utf8"))
                        print ("[+] thread disconnected for "+ip+":"+str(port))
                        fd = self.socket.fileno()
                        lock.acquire()
                        del sendqueues[fd]
                        userfdmap.remove(userfd)
                        lock.release()
                        sys.exit()

                    elif "broadcast message" in command.decode("utf8"):
                          message = command.partition(bytes(" ","utf8"))
                          messagef = message[2].partition(bytes(" ","utf8"))

                          msg = userdata + ": " + messagef[2].decode("utf8")
                          lock.acquire()
                          for  q in sendqueues.values():
                              q.put(msg)
                          lock.release()
                          ack = "broadcasted"
                          self.socket.send(bytes(ack,"utf8"))
                    else:
                          error = "Invalid command. Please enter a proper one"
                          self.socket.send(bytes(error,"utf8"))



        lock.acquire()
        curusers.remove(userdata)
        lock.release()
        offlinedata = userdata + " " + str(logtime)
        lock.acquire()
        offlineusers.append(offlinedata)
        lock.release()
        print (offlinedata , "removed")
        print ("logged out")
        sys.exit()

class ClientThreadread(Thread):
    def __init__(self,sock):
        Thread.__init__(self)

        self.sock = sock

        print ("New thread for chat relying started")







    def run(self):


         tcpsock2.listen(1)
         (conn2, addr) = tcpsock2.accept()
         welcomemsg = bytes("hi",'utf8')
         conn2.send(welcomemsg)
         chat = "initial"
         #print ("ind here is")
         print (self.sock.fileno())
         while True:
             for p in userfdmap:           #userfdmap contains mapping between usernames and their socket's file despcriptor which we use as index to access their respective queue
                 if str(self.sock.fileno()) in p:
                     #print("connection present")
                     connectionpresent = 1
                 else:
                     #print("connection not present")
                     connectionpresent = 0         #We will use this to implement other features - no use as of now



             try:
                 chat = sendqueues[self.sock.fileno()].get(False)

                 print (chat)
                 conn2.send(bytes(chat,"utf8"))
             except queue.Empty:

                 chat = "none"
                 time.sleep(2)
             except KeyError as e:
                 pass




threads = []

while True:
    tcpsock.listen(6)
    print("csce513Msg Server!")
    print ("Waiting for incoming connections...")
    (conn, (ip,port)) = tcpsock.accept()
    q = queue.Queue()
    lock.acquire()


    sendqueues[conn.fileno()] = q
    lock.release()


    print ("new thread with " , conn.fileno())
    newthread = ClientThread(conn,ip,port)
    newthread.daemon = True
    newthread.start()
    newthread2 = ClientThreadread(conn)
    newthread2.daemon = True

    newthread2.start()
    threads.append(newthread)
    threads.append(newthread2)



for t in threads:
    t.join()

    print ("eND")
