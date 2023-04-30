import socket
from abc import ABC, abstractmethod
from codecs import unicode_escape_decode


class Connection:
  '''
  The Connection class encapsulates the connection set up by the socket.
  Fields:
    conn: the socket connection (after client calls connect() or server calls accept())
    identity: a tuple of (role, channel) where role is either "client" or "server" and channel is either "control" or "data"
              used for error checking so that the data channel is set up by the correct designated function for each side
  Methods: extend the sending and receiving functionality of the socket
  '''
  def __init__(self, *, conn):
    self.conn = conn
    self._identity = None

  def __del__(self):
    self.conn.close()
    # specify which connection is closed
    print("{} connection closed.".format(self.identity))
  '''
  Abstract class: implemented by the clientConnection and serverConnection classes
  '''
  @abstractmethod
  def init_data_channel(self):
    """
    Function to initialize the data channel for the client side.
    """
    pass

  @property
  def identity(self):
    return self._identity

  @identity.setter
  def identity(self, id):
    self._identity = id

  '''
  Function to format the message according to the designated format
  Message format: 10 bytes of header information + data
  '''
  def send_message(self, data):
    # set header to 10 bytes
    size = len(data)
    data_size = size.to_bytes(10, byteorder='big')

    data = data_size + data
    
    data_sent = 0

    # ensure all data is sent
    while data_sent != len(data):
      data_sent += self.conn.send(data[data_sent:])

     
  '''
  Function to receive the specified amount of data from the connected socket.
  '''
  def recvAll(self, numBytes):
    recvBuff = b''
    tmpBuff = b''
    # ensure all data has been received
    while len(recvBuff) < numBytes:
      tmpBuff = self.conn.recv(numBytes)
      # The other side has closed the socket
      if not tmpBuff:
        break
      recvBuff += tmpBuff
      
    return recvBuff
      
  '''
  Function to receive header information and convert it to an integer before
  calling recvAll(file_size) to get the data payload. 
  '''
  def recv_data_payload(self):
    data = ""
    file_size = 0	
    file_size_buff = ""
    #receive header size
    file_size_buff = self.recvAll(10)

    #initialize buffer for file
    if file_size_buff:
      file_size = int.from_bytes(file_size_buff, byteorder='big')

    # receive a file given a file size
    data = self.recvAll(file_size)
    return data

  
    
class clientConnection(Connection):
  '''
  TODO: [description]
  '''
  def init_data_channel(self):
    # Read the message for the port number of the data channel from the server
    server_data_connect_port = self.recv_data_payload().decode()
    server_data_socket = (self.conn.getpeername()[0], int(server_data_connect_port))

    # Create new socket and connect to the server over the data channel
    client_data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_data_socket.connect(server_data_socket)
    return client_data_socket


class serverConnection(Connection):
  '''
  TODO: [description]
  '''
  def init_data_channel(self):
    welcoming_data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcoming_data_sock.bind(('', 0))

    # Notify the client about the newly created socket for data transfer
    # send back only the port number because the client already knows the IP address
    server_data_sock_port =  str((welcoming_data_sock.getsockname())[1])
    self.send_message(server_data_sock_port.encode())

    # Wait for the client to connect to the welcoming socket
    welcoming_data_sock.listen(1)

    # Accept connections and return the socket data connection
    # Note: data_conn is the socket connection, and addr is the address of the client
    data_conn, addr = welcoming_data_sock.accept()
    return data_conn