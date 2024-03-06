import socket
import time

HEADER = 64                                                     # the first message the client sends to the server will be the length of the message
PORT = 5050                                                     # port that we are going to use
SERVER = '192.168.1.29'
#SERVER = socket.gethostbyname(socket.gethostname())             # get the ip address of the server
ADDR = (SERVER, PORT)                                           # tuple of the server and port
FORMAT = 'utf-8'                                                # format of the message
DISCONNECT_MESSAGE = "!DISCONNECT"                              # message to disconnect

client =socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # create a socket object
client.connect(ADDR)                                            # connect to the server

def send(msg):
    message = msg.encode(FORMAT)                                # encode the message
    msg_length = len(message)                                   # get the length of the message
    send_length = str(msg_length).encode(FORMAT)                # encode the length of the message
    send_length += b' ' * (HEADER - len(send_length))           # add spaces to the length of the message to make it 64 bytes
    client.send(send_length)                                   
    client.send(message)                                        # send the message

send("Hello World!")
send("Starting transmiting data...")
i=0
while True:
    time.sleep(1)
    send(f"Data number {i}")
    i+=1