# Echo client program
import socket

HOST = 'localhost'    # The remote host
PORT = 50007              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, world'*100)
    r = b''
    while True:
        data = s.recv(1024)
        print(data)
        if not data: break
        r += data
print('Received', repr(data))
