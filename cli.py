import socket
import sys
from Connection import *
from ftp.client import ftp_client

# Command line checks 
if len(sys.argv) < 2:
  print ("USAGE python " + sys.argv[0] + " <FILE NAME>" )

# Server address and port 
serverAddr = sys.argv[1]
serverPort = int(sys.argv[2])
print("Server address: " + serverAddr + ", server port: " + str(serverPort))


# TCP control channel setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((serverAddr, serverPort))
control_channel = clientConnection(conn = client_socket)
control_channel.identity = "Control"

# After control channel is established, create a client object
client = ftp_client(control_channel, None)
client.taking_request()

client_socket.close()
del control_channel
del client