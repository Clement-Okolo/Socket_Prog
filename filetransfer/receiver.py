# import module
import os
import socket
import time

print("csce513Msg Reciever!")
host = input("Enter Sender IP: ")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Trying to connect to socket
try:
    sock.connect((host, 3000))
    print("Connected Successfully")
except:
    print("Unable to connect")
    exit(0)

# recieve file details
file_name = sock.recv(100).decode()
file_size = sock.recv(100).decode()

# Opening and writing file.
with open("./rec/" + file_name, "wb") as file:
    c = 0
    # Starting the time capture
    start_time = time.time()

    # Running the loop while file is recieved
    while c <= int(file_size):
        data = sock.recv(1024)
        if not (data):
            break
        file.write(data)
        c += len(data)

    # Ending the time capture
    end_time = time.time()

print("File Transfer Complete! Total time: ", end_time - start_time)

# Closing the socket
sock.close()