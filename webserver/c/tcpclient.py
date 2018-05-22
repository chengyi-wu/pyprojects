import socket

def connect(host, port):
    s = socket.socket()
    s.connect((host, port))
    return s

def read(fd):
    size = 1024
    data = ''
    while True:
        buf = fd.recv(size)
        data += buf.decode('utf-8')
        if len(buf) == 0:
            break
    print(data)

def write(fd, data):
    data = data.encode('utf-8')
    fd.send(data)

def close(fd):
    fd.close()
    

if __name__ == '__main__':
    while True:
        line = input(">> ")
        fd = connect("localhost", 8080)
        if fd == -1:
            print("Failed to connect!")
            break
        write(fd, line + '\r\n')
        read(fd)
        
        close(fd)