# Simplified FTP Protocol

Involves socket programming to transfer file data between a client and a server. The implementations of ftp client and ftp server are in ftp folder under client.py and server.py respectively. The client and server communicate over a TCP connection. The client and server are able to transfer files to and from each other over a separate data channel. <br>

Socket connection is encapsulated inside a Connection object, implemented inside Connection.py. All functionalities of a socket connection (send, receive) are handled by the Connection object. <br>

Data Channel is teardown after each file transfer. <br>
Control Channel is teardown after the client issues a QUIT command. <br>

## Name:
Nghia Phan - email: ptnghia@csu.fullerton.edu


## Programming Language

- Python 3

## Usage
### !IMPORTANT: Server started before client
### Server

Invoke server.py by:

```
python3 serv.py [server_port]
```

The server process will log to standard output

It is recommended to start the client and server processes in different terminals side by side to see the full operation of the FTP implementation
### Client

1. Invoking client.py by:

```
python3 cli.py [server_id] [server_port]
for this assignment: server_id = localhost
```

an ftp> prompt will appear
```
ftp> [command]
```

under the ftp> prompt, the user can issue the following commands (all lowercase commands):
```
ftp> get [filename]
```
  - to retrieve [filename] file from the server (currently under folder server_files)
```
ftp> put [filename]
```
  - to send the [filename] file from the client to the server (file originally under folder client_files)
```
ftp> ls
```
  - to list all files in the server directory

``` 
ftp> quit
```
  - to end the ftp session


