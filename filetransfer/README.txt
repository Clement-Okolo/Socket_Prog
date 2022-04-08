**File transfer**

One core functions is implemented:

1. client transfer a file to another client

To run the script, simply download it and save it at a convenient location on your computer.
Both the server and client script can then be run from the Command prompt (in Windows) 
or from bash terminal (Linux users) by simply typing "python server.py" and "python client.py"

After file is transfered, connection between sender and receiver is terminated. 
You would need to run the script again to send subsequent files.
You do not need to enter port number along with IP address.
Port number is automatically set to 3000 for convenient.

How to run sender file :
$ python sender.py
Enter file name

How to run reciever file:
$ python receiver.py
Enter sender IP '127.0.0.1'