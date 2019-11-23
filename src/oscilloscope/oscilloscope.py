import socket


class Oscilloscope:

    def __init__(self, ip, port=5025):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))
        self.connection.setblocking(0)

    def close(self):
        self.connection.close()
