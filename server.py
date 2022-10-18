import select
import socket
import struct
import queue
import threading
import time
from protocol import *

IDROBOT = 1

IDQR = 1
IDRED = 2
IDSTOP = 3

class SocketServer(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.sock = None
        self.inputs = []
        self.outputs = []
        self.message_queues = {}
        self.online = threading.Event()
        self.protocol = Protocol()
        self.daemon = True

    def startServer(self):
        if not self.online.is_set():
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setblocking(0)
            self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(10)
            self.inputs.append(self.sock)
            self.online.set()
            print("Server is online.")
            self.start()

    def _recv_n_bytes(self, n, s):
        """ Convenience method for receiving exactly n bytes from
            self.socket (assuming it's open and connected).
        """
        data = ''
        while len(data) < n:
            chunk = s.recv(n - len(data)).decode()
            if chunk == '':
                break
            data += chunk
        return data

    def receive(self, s):
        try:
            header_data = self._recv_n_bytes(4, s).encode()
            if len(header_data) == 4:
                msg_len = struct.unpack('<L', header_data)[0]
                data = self._recv_n_bytes(msg_len, s)
                if len(data) == msg_len:
                    print("Received %s from %s" %(data, s.getpeername()))
                    self.message_queues[s].put(header_data.decode() + data)
                    if s not in self.outputs:
                        self.outputs.append(s)

                    #self.inputs.remove(s) #Remove disposable client sockets for now
                    return
            else:
                if s in self.outputs:
                    self.outputs.remove(s)
                    s.close()
                    del self.message_queues[s]
        except IOError as e:
            pass

    def run(self):
        while self.inputs:
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)
            for s in writable:
                try:
                    next_msg = self.message_queues[s].get_nowait()
                except queue.Empty:
                    self.outputs.remove(s)
                except KeyError: #HANDLE IT LATER
                    pass
                else:
                    s.sendall(next_msg.encode())   #Works like a echo-server for now
                    #self.outputs.remove(s) #Remove disposable client sockets for now

            for s in exceptional:
                print("Exception for %s" %(s.getpeername()))
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
                del self.message_queues[s]

            for s in readable:
                if s is self.sock:
                    conn, addr = s.accept()
                    conn.setblocking(0)
                    self.inputs.append(conn)
                    self.message_queues[conn] = queue.Queue()

                else:
                    self.receive(s)
            

            if not self.online.is_set():
                self.inputs.remove(self.sock)
                self.sock.close()
                break


if __name__ == "__main__":
    server = SocketServer("localhost", 50000)
    server.startServer()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break