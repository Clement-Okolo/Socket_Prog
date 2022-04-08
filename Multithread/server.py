import socket
import threading

IP = "127.0.0.1"    # server IP
PORT = 3000         # server port
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        if msg == DISCONNECT_MSG:       # if server receives "!DISCONNECT" message
            connected = False           # disconnect client

        print(f"[{addr}] {msg}")        # receive message from client
        msg = f"Msg received: {msg}"    # send message back to client

        conn.send(msg.encode(FORMAT))

    conn.close()

def main():
    print("csce513Msg Server!")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create server socket
    server.bind(ADDR)
    server.listen()
    print("Waiting for connection...")

    while True:
        conn, addr = server.accept()    # accept connection from client
        thread = threading.Thread(target=handle_client, args=(conn, addr))  # create thread
        thread.start()                  # start thread
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")    # number of thread

if __name__ == "__main__":
    main()