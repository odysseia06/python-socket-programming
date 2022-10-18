import socket
import struct
import threading
import queue
import select
import time
import random

IS_CONNECTED = threading.Event()

class ContinuousClient(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.connected = threading.Event()
        self.alive = threading.Event()
        self.started = threading.Event()
        self.alive.set()
        self.socket = None
        self.daemon = True
        self.command_queue = queue.Queue()
        self.reply_queue = queue.Queue()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print("Connection attempt.")
            self.socket.connect((self.host, self.port))
            print("Connection with server is made.")
            self.socket.setblocking(0)
            self.connected.set()
            if not self.started.is_set():
                self.start()
                self.started.set()
        except ConnectionRefusedError:
            print("Connection refused.")
            pass
        except TimeoutError:
            print("Timeout error.")
            pass
        

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

    def run(self):
        while self.alive.is_set():
            try:
                r,_,_ = select.select([self.socket], [], [])
                if r:
                    header_data = self._recv_n_bytes(4, self.socket).encode()
                    if len(header_data) == 4:
                        msg_len = struct.unpack('<L', header_data)[0]
                        data = self._recv_n_bytes(msg_len, self.socket)
                        if len(data) == msg_len:
                            self.reply_queue.put(data)
            except Exception as e:
                self.connected.clear()
                self.alive.clear()
                #print(e)
                

    def send(self, message):
        try:
            header = struct.pack('<L', len(message))
            self.socket.sendall(header + message.encode())
        except:
            pass

    def join(self, timeout=None):
            self.alive.clear()
            threading.Thread.join(self, timeout)

        
class DisposableClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
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

    def connect_and_get(self, message, delay=None):
        if delay:
            time.sleep(delay)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        header = struct.pack('<L', len(message))
        try:
            s.sendall(header + message.encode())

            header_data = self._recv_n_bytes(4, s).encode()
            if len(header_data) == 4:
                msg_len = struct.unpack('<L', header_data)[0]
                data = self._recv_n_bytes(msg_len, s)
                if len(data) == msg_len:
                    return data
        except IOError as e:
            print(str(e))
            return None

        s.shutdown()


def disposable_client_send_loop():
    ds = DisposableClient("localhost", 50000)
    count = 0
    while True:
        try:
            print(ds.connect_and_get("Hello"+str(count)))
            count += 1
        except KeyboardInterrupt:
            break
            
def continuous_client_send_loop():
    cs = ContinuousClient("localhost", 50000)
    count = 0
    cs.connect()
    while True:
        try:
            cs.send("Hello"+str(count))
            count += 1
            print(cs.reply_queue.get())
        except KeyboardInterrupt:
            break



if __name__ == "__main__":
    t1 = threading.Thread(target=continuous_client_send_loop, args=())
    t2 = threading.Thread(target=continuous_client_send_loop, args=())
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
        