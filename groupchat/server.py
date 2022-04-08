import threading
import socket

# define host and port for server
host = "127.0.0.1" # localhost
port = 3000

# start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen() # server starts listening for incomming connection

# define two empty list
clients = []    # new clients are added here
nicknames = []  # nicknames of clients are added here

# define broadcast method
def broadcast(message):
    for client in clients:
        client.send(message) # sends a message to all clients connected to the server

# define handle method for client connection: recv msg from a client and send msg to all clients
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname= nicknames[index]
            broadcast(f"{nickname} left the chat".encode('ascii'))
            nicknames.remove(nickname)
            break

# define recieve method combines all method into a main method
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send("NICK".encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of the client is {nickname}!")
        broadcast(f"{nickname} joined the group chat".encode('ascii'))
        client.send("Connected to the server!".encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("csce513Msg Server!")
print("Waiting for connection...")
receive()


