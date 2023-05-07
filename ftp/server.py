import socket
import sys
import subprocess
import os

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
  
      if request != 'quit':
        server_data_socket = self.control_channel.init_data_channel()
        data_channel = serverConnection(conn = server_data_socket)
        data_channel.identity = "Data"
        self.data_channel = data_channel

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

      if request != 'quit':
        self.data_channel = None
        #Note: close must be called to destroy the reference to socket connection
        server_data_socket.close()
        del data_channel

      print(" \n")

  def serve_get_request(self):
      # Receive the file name from the client
      file_name = self.data_channel.recv_data_payload().decode()

      oldwd = os.getcwd()
      os.chdir("server_files")
      with open(file_name, 'rb') as f:
        data = f.read(1024)
        while data:
          self.data_channel.send_message(data)
          data = f.read(1024)
      
      print("File sent successfully")
      os.chdir(oldwd)
  
  def serve_put_request(self):
      # Receive the file name from the client
      file_name = self.data_channel.recv_data_payload().decode()
      print("Receiving file: " + file_name)
      # Upload the file from the server over the data channel
      # and save it to the current working directory
      # check if the file exists, if it does append number to the end
      # of the file name
      oldwd = os.getcwd()
      try:
        os.chdir("server_files")
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
      finally:
        os.chdir(oldwd)
      
      print("File received successfully")
      
  
  def serve_ls_request(self):
      # Send the list of files to the client
      oldwd = os.getcwd()
      os.chdir("server_files")
      listOfFiles = ""
      for line in subprocess.getoutput("ls"):
        listOfFiles += line
      self.data_channel.send_message(listOfFiles.encode())

      os.chdir(oldwd)
      print("List of files sent successfully")
  
  def serve_quit_request(self):
      # Inform the client that the server is closing the connection
      self.control_channel.send_message("Server closed connection".encode())
      self.control_channel = None