import socket
import sys
import os
from time import sleep
from ftp.server import ftp_server

from Connection import *

# The port on which to listen
listenPort = int(sys.argv[1])

# Create a welcome socket. 
welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcomeSock.bind(('', listenPort))
while True:
  # Servicing at most 1 client at a time
  print ("Waiting for new connection...")
  welcomeSock.listen(1)
      
  # Accept connections
  control_conn, addr = welcomeSock.accept()
  control_channel = serverConnection(conn = control_conn)
  control_channel.identity = "Control"
  server = ftp_server(control_channel, None)
    
  print ("Accepted connection from client: ", addr)
  print ("\n")

  server.serving_request()
  # delete the reference to the control channel and the server objects
  # Note: close must be called to completely destroy all references to the connection
  control_conn.close()
  del control_channel
  del server

  sleep(0.3)