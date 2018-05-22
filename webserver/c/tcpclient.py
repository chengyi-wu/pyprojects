import socket
import sys

def connect(host, port):
    s = socket.socket()
    s.connect((host, port))
    return s

def read(fd):
    size = 1024
    data = ''
    buf = fd.recv(size)
    data = buf.decode('utf-8')
    print(data[:-2])

def write(fd, data):
    data = data.encode('utf-8')
    fd.send(data)

def close(fd):
    fd.close()
    

if __name__ == '__main__':
    fd = connect(sys.argv[1], int(sys.argv[2]))
    if fd == -1:
        print("Failed to connect!")
    while True:
        line = input(">> ")
        write(fd, line + '\0')
        read(fd)
