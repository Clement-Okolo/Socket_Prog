# This file is used for sending the file over socket
import os
import socket
import time

host = "127.0.0.1"
port = 3000

# Creating a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen(5)
print("csce513Msg Sender!")
print("Host Name: ", sock.getsockname())


# Accepting the connection from receiver client
client, addr = sock.accept()

# Getting file details
file_name = input("File Name:")
file_size = os.path.getsize((file_name))

# Sending file_name and detail
client.send(file_name.encode())
client.send(str(file_size).encode())

# Opening file and read data
with open(file_name, "rb") as file:
    c = 0
    # Starting the time capture.
    start_time = time.time()

    # Running loop while c != file_size
    while c <= file_size:
        data = file.read(1024)
        if not (data):
            break
        client.sendall(data)
        c += len(data)

    # Ending the time capture
    end_time = time.time()

print("File Transfer Complete! Total time: ", end_time - start_time)

# Closing the socket.
sock.close()