import socket
import StringIO
import sys
import traceback
import os
import errno
import signal

class WSGIServer(object):

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5
    
    def __init__(self, server_address):
        print('DEBUG\tWSGIServer::__init__')
        # Create a listening socket
        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )
        # Allow to reuse the same address
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind
        listen_socket.bind(server_address)
        # Activate
        listen_socket.listen(self.request_queue_size)
        # Get server host name and port
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        # Return headers set by Web framework/Web application
        self.headers_set = []

    def set_app(self, application):
        print('DEBUG\tWSGIServer::set_app')
        self.application = application

    def grim_reaper(self, signum, frame):
        pid, status = os.wait()
        print(
            'Child {pid} terminated with status {status}\n'.format(pid=pid, status=status)
        )

    def serve_forever(self):
        print('DEBUG\tWSGIServer::serve_forever')
        listen_socket = self.listen_socket

        signal.signal(signal.SIGCHLD, self.grim_reaper)

        while True:
            try:
                # New client connection
                self.client_connection, client_address = listen_socket.accept()
            except IOError as e:
                code, msg = e.args
                if code == errno.EINTR:
                    continue
                else:
                    raise

            pid = os.fork()
            if pid == 0: # chlid
                listen_socket.close() # close the parent copy
                # Handle one request and close the client connection. Then
                # loop over to wait for another client connection.
                self.handle_one_request()
                os._exit(0)
            else: # parent
                self.client_connection.close() # close 

    def handle_one_request(self):
        print('DEBUG\tWSGIServer::handle_one_request')
        self.request_data = request_data = self.client_connection.recv(1024)
        # Print formated request data a la 'curl -v'
        print(''.join(
            '< {line}\n'.format(line=line)
            for line in request_data.splitlines()
        ))

        self.parse_request(request_data)

        # Construct enviroment dictionary using request data
        env = self.get_environ()

        # It's time to call our application callable and get
        # back a result that will become HTTP response body
        print('DEBUG\tWSGIServer::handle_one_request:start_response')
        result = self.application(env, self.start_response)
        
        # Contruct a response and send it back to the client
        print('DEBUG\tWSGIServer::handle_one_request:finish_response')
        self.finish_response(result)

    def parse_request(self, text):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip('\r\n')
        # Break down the request line into components
        (self.request_method, # GET
         self.path,           # /hello
         self.request_version # HTTP/1.1
        ) = request_line.split()

    def get_environ(self):
        env = {}

        # PEP8 convertions
        #
        # Required WSGI variables
        env['wsgi.version']         = (1, 0)
        env['wsgi.url_scheme']      = 'http'
        env['wsgi.input']           = StringIO.StringIO(self.request_data)
        env['wsgi.errors']          = sys.stderr
        env['wsgi.multithread']     = False
        env['wsgi.multiprocess']    = False
        env['wsgi.run_one']         = False
        
        # Required CGI variables
        env['REQUEST_METHOD']       = self.request_method
        env['PATH_INFO']            = self.path
        env['SERVER_NAME']          = self.server_name
        env['SERVER_PORT']          = str(self.server_port)

        return env
    
    def start_response(self, status, response_headers, exec_info=None):
        traceback.print_stack()
        # Add necessary server headers
        server_headers = [
            ('Date', 'Mon, 10 Jul 2017, 21:15:00 GMT+8'),
            ('Server', 'WSGIServer 0.2'),
        ]

        self.headers_set = [status, response_headers + server_headers]

        # To adhere to WSGI specification the start_response must resturn
        # a 'write' callable.
        # return self.finish_response

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = 'HTTP/1.1 {status}\r\n'.format(status=status)
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in result:
                response += data
            
            print(''.join(
                '> {line}\n'.format(line=line)
                for line in response.splitlines()
            ))
            self.client_connection.sendall(response)
        finally:
            self.client_connection.close()

SERVER_ADDRESS = (HOST, PORT) = '', 8888

def make_server(server_address, applicaiton):
    print('global::make_server')
    print(server_address, application)
    server = WSGIServer(server_address)
    server.set_app(applicaiton)
    return server

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as modle:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
    httpd.serve_forever()
    
