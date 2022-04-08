"""Client to Client Communication"""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

HOST = "127.0.0.1"
PORT = 3000
BUFSIZ = 1024
ADDR = (HOST, PORT)

clients = {}
addresses = {}

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)
f = open('test.png','wb')

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()        # server accepts connection to client
        print("%s:%s has connected." % client_address)
        client.send(bytes("Enter Username:", "utf8"))   
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()    # create thread

def handle_client(client):  # Takes client socket as argument
    """Handles a single client connection"""

    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! You can start chatting now!' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s Joined The Chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)          # server receives message from client
        if msg != "{quit}":
            broadcast(msg, name+": ")      # broadcast message to client
        else:
            #print("quit pressed")
            client.send(bytes("{quit}","utf8"))
            client.close()                  # close conncetion with client
            del clients[client]
            broadcast("%s has left the chat." % name) # Notification to other clients 
            break

def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)    # send message to client

if __name__ == "__main__":
    SERVER.listen(5)
    print("csce513Msg Server!")
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()

