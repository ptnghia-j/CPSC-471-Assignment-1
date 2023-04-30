import socket
import sys
import os

# append the path to the parent directory to import the Connection class
sys.path.append('../')

from Connection import *

class ftp_client:
  '''
  The ftp_client class encapsulates the client side of the FTP application. \n
  Fields:
    control_channel: the encapsulation of control connection from client side
    data_channel: the encapsulation of data connection from client side
  '''
  def __init__(self, control_channel, data_channel):
    self.control_channel = control_channel
    self.data_channel = data_channel
    print("FTP client control channel established. Ready to take requests.")

  def __del__(self):
    print("FTP client closed.")

  '''

  '''
  def taking_request(self):
    while True:
      user_input =input("ftp> ").split()

      # Notify the server about the type of request through the control channel
      request = user_input[0]
      self.control_channel.send_message(request.encode())

      if request != 'quit':
        client_data_socket = self.control_channel.init_data_channel()
        data_channel = clientConnection(conn = client_data_socket)
        data_channel.identity = "Data"
        self.data_channel = data_channel

      if request == "get":
        file_name = user_input[1]
        self.serve_get_request(file_name)

      elif request == "put":
        file_name = user_input[1]
        self.serve_put_request(file_name)

      elif request == "ls":
        self.serve_ls_request()

      elif request == "quit":
        self.serve_quit_request()
        break
      
      else:
          print("Invalid command. Please try again.")
          
      if request != 'quit':
        self.data_channel = None
        #Note: close must be called to destroy the reference to socket connection
        client_data_socket.close()
        del data_channel

      print(" \n")

  '''
  '''     
  def serve_get_request(self, file_name):
    # Send the file name to the server
    self.data_channel.send_message(file_name.encode())
    print("Receiving file: " + file_name)

    # Download the file from the server over the data channel
    # and save it to the current working directory
    # check if the file exists, if it does append number to the end
    # of the file name
    try:
      if os.path.exists(file_name):
        i = 1
        f_name, f_ext = os.path.splitext(file_name)
        new_name = '{}_{}{}'.format(f_name, i, f_ext)
        while os.path.exists(new_name):
          i += 1
          new_name = '{}_{}{}'.format(f_name, i, f_ext)
        file_name = new_name
      with open(file_name, 'wb') as f:
        while True:
          data = self.data_channel.recv_data_payload()
          if not data:
              break
          f.write(data)
      print("File transfer complete.")

    except socket.error as s_error:
      print("Socket error: " + str(s_error))
          
      
  '''
  '''
  def serve_put_request(self, file_name):
    # Send the file name to the server
    self.data_channel.send_message(file_name.encode())
    print("Sending file: " + file_name)

    try:
      with open(file_name, 'rb') as f:
        # Send 1024 bytes of data at a time
        total_bytes_sent = 0
        data = f.read(1024)
        while data:
            self.data_channel.send_message(data)
            data = f.read(1024)
            print("data: " + str(data) + "\n")
            total_bytes_sent += len(data)
      print("File transfer complete. Send total of " + str(total_bytes_sent) + " bytes.")

    except socket.error as s_error:
      print("Socket error: " + str(s_error))


  '''
  '''
  def serve_ls_request(self):
    # Receive the list of files from the server over the data channel
    # and print it to the screen
    while True:
      file = self.data_channel.recv_data_payload().decode()
      if not file:
        break
      print(file)

    print("File list transfer complete.")
  

  '''
  '''
  def serve_quit_request(self):
    # No need to establish a data channel for this request
    # Wait for server to reply with "quit"
    sever_message = self.control_channel.recv_data_payload().decode()
    print(sever_message)



if __name__ == "__main__":                 
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

  # no need to delete the referenced objects, they will be deleted automatically when the program terminates
  client_socket.close()
  del control_channel
  del client