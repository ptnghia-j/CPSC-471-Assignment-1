import socket
import sys
import subprocess
import os
from time import sleep

# append the path to the parent directory to import the Connection class
sys.path.append('../')

from Connection import *

class ftp_server:
  def __init__(self, control_channel, data_channel):
    self.control_channel = control_channel
    self.data_channel = data_channel
    print("FTP server control channel established. Ready to take requests.")

  def __del__(self):
    pass

  def serving_request(self):
    while True:
      # Read the message to find out about the type of request
      request = self.control_channel.recv_data_payload().decode()
  
      if request == "get":
        self.serve_get_request()

      elif request == "put":
        self.serve_put_request()

      elif request == "ls":
        self.serve_ls_request()

      elif request == "quit":
        self.serve_quit_request()
        break
      else:
        print("Something wrong")
        break

      print(" \n")

  def serve_get_request(self):
      server_data_socket = self.control_channel.init_data_channel()
      data_channel = serverConnection(conn = server_data_socket)
      data_channel.identity = "Data"
      self.data_channel = data_channel

      # Receive the file name from the client
      file_name = self.data_channel.recv_data_payload().decode()
      with open(file_name, 'rb') as f:
        data = f.read(1024)
        while data:
          self.data_channel.send_message(data)
          data = f.read(1024)
      
      print("File sent successfully")
      # Close the data connection
      self.data_channel = None
      del self.data_channel

  
  def serve_put_request(self):
      server_data_socket = self.control_channel.init_data_channel()
      data_channel = serverConnection(conn = server_data_socket)
      data_channel.identity = "Data"
      self.data_channel = data_channel

      # Receive the file name from the client
      file_name = self.data_channel.recv_data_payload().decode()
      print("Receiving file: " + file_name)
      # Upload the file from the server over the data channel
      # and save it to the current working directory
      # check if the file exists, if it does append number to the end
      # of the file name
      try:
        if os.path.exists(file_name):
          i = 1
          f_name, f_ext = os.path.splitext(file_name)
          while os.path.exists(file_name):
            file_name = "{}_{}{}".format(f_name, i, f_ext)
            i += 1
        with open(file_name, 'wb') as f:
          data = self.data_channel.recv_data_payload()
          while data:
            f.write(data)
            data = self.data_channel.recv_data_payload()
      except socket.error as e:
        print("Error receiving file: " + str(e))
      
      print("File received successfully")
      # Close the data connection
      self.data_channel = None
      del self.data_channel
  
  def serve_ls_request(self):
      server_data_socket = self.control_channel.init_data_channel()
      data_channel = serverConnection(conn = server_data_socket)
      data_channel.identity = "Data"
      self.data_channel = data_channel
      
      # Send the list of files to the client
      listOfFiles = ""
      for line in subprocess.getoutput("ls"):
        listOfFiles += line
      self.data_channel.send_message(listOfFiles.encode())
      print("List of files sent successfully")

      # Close the data connection
      self.data_channel = None
      del self.data_channel
  
  def serve_quit_request(self):
      # Inform the client that the server is closing the connection
      self.control_channel.send_message("Server closed connection".encode())
      self.control_channel = None
      
if __name__ == "__main__":
   
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
    del control_channel
    del server

    sleep(0.3)



