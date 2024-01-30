import socket

class SocketConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def send_data(self, data):
        message = bytes(data, 'utf-8')
        self.socket.sendall(message)

    def close(self):
        if self.socket:
            self.socket.close()

