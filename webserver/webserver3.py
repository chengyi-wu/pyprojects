import os
import socket
import time
import signal
import errno

SERVER_ADDRESS = (HOST, PORT) = ('', 8888)
REQUEST_QUEUE_SIZE = 5

def grim_reaper(signum, frame):
    pid, status = os.wait()
    print(
        'Child {pid} terminated with status {status}\n'.format(pid=pid, status=status)
    )

def handle_request(client_connection):
    request = client_connection.recv(1024)
    print(request.decode())
    http_response = '''\
    HTTP/1.1 200 OK

    Hello, world!
    '''

    client_connection.sendall(http_response)
    print('DEBUG\tSlepping for 6s...')
    time.sleep(6)

def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port} ...'.format(port=PORT))

    signal.signal(signal.SIGCHLD, grim_reaper)
    
    while True:
        try:
            client_connection, client_address = listen_socket.accept()
        except IOError as e:
            code, msg = e.args
            if code == errno.EINTR: # Raised by the exit of the child process
                continue
            else:
                raise
        # fork() deosn't work for Windows...
        pid = os.fork()
        if pid == 0: # child
            listen_socket.close() # close the child copy of the listen_socket
            handle_request(client_connection)
            client_connection.close() # close the client_connection
            os._exit(0) #child exits
        else: #parent
            client_connection.close() # close the parent copy of the listen_socket

if __name__ == '__main__':
    serve_forever()