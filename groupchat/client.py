import threading
import socket

# define host and port for server
host = "127.0.0.1" # localhost
port = 3000

# choose a username
username = input("Enter Username: ")

# define socket for client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port)) # connect instead of bind

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')    # recieve message
            if message == 'NICK':
                client.send(username.encode('ascii'))      # send client username
            else:
                print(message)
        except:
            print("An error occured!")
            client.close()                                 # close client connection
            break

def write():
    while True:
        message = f'{username}: {input("")}' 
        client.send(message.encode('ascii'))       # send message from client

receive_thread = threading.Thread(target=receive)  # create thread for receive
receive_thread.start()      # start thread

write_thread = threading.Thread(target=write)      # create thread for start
write_thread.start()        # start thread

