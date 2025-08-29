import socket
import json
from logger import Logger


class UdpJsonSender:
    def __init__(self, ip: str, port: int):
        self.address = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.log = Logger.get()

    def send(self, data: dict):
        try:
            message = json.dumps(data).encode('utf-8')
            self.sock.sendto(message, self.address)
        except Exception as e:
            self.log.error(f"Error while sending payload: {e}")

    def close(self):
        self.sock.close()