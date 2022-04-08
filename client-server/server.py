#import socket module
from os import system
import select
import socket

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 3000

# Create TCP server socket
#(AF_INET is used for IPv4, while SOCK_STREAM is used for TCP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the local port and connection address
server_socket.bind((IP, PORT))

# Listen for client connection
server_socket.listen()
print("csce513Msg Server!")
print("Waiting for connection...")

sockets_list = [server_socket]                  # list of client sockets

# dictionary to store clients
clients = {}    # client socket is key, userdata is value


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}

    except:
        return False


while True:
    # Advanced Client
    ''' Add the functionality to allow a client to send and receive messages at the
same time with less CPU workload using I/O multiplexing, select()'''

    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:        # if new client connection
            client_socket, client_address = server_socket.accept()  # accept connection with client

            user = receive_message(client_socket)   # receive client message
            if user is False:                       # client unavailable or disconnects
                continue

            sockets_list.append(client_socket)      # add client socket to list
            
            clients[client_socket] = user           # add new user to clients dictionary

            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")
        else:
            message = receive_message(notified_socket) # if user is an existing user

            if message is False:
                print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
    
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]

