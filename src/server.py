# multiconn-server.py

import sys
import socket
import selectors
import types
import threading
import ctypes
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

class server_thread(threading.Thread):

    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.sel = selectors.DefaultSelector()
        self.host = host
        self.port = port

    def __accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, outbound=b"", name="Unregistered")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def __service_connection(self, key, mask):
            sock = key.fileobj
            data = key.data
            if mask & selectors.EVENT_READ:
                recv_data = sock.recv(1024)  # Should be ready to read
                if recv_data:
                    data.outbound += recv_data
                else:
                    print(f"Closing connection to {data.addr}")
                    self.sel.unregister(sock)
                    sock.close()
            if mask & selectors.EVENT_WRITE:
                if data.outbound:
                    print(f"Echoing {data.outbound!r} to {data.addr}")
                    sent = sock.send(data.outbound)  # Should be ready to write
                    data.outbound = data.outbound[sent:]

    def run(self):
        print("Starting server...")
        host = self.host
        port = self.port
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_sock.bind((host, port))
        listen_sock.listen()
        print(f"Listening on {(host, port)}")
        listen_sock.setblocking(False)
        data = types.SimpleNamespace(addr=(host, port), outbound=b"", name="Listening Socket")
        self.sel.register(listen_sock, selectors.EVENT_READ, data=data)
        while True:
            if shutdown_event.is_set():
                print("Shutting down the server...")
                self.sel.close()
                break
            events = self.sel.select(timeout=-1)
            for key, mask in events:
                if key.data.name is "Listening Socket":
                    # when data is None, the event came from the listening socket
                    self.__accept_wrapper(key.fileobj)
                else:
                    # when data is defined, the event came from a client socket
                    self.__service_connection(key, mask)

    def current_connections(self):
        conns = self.sel.get_map().values()
        conns_info = [c.data for c in conns]
        conns_names = [ci.name for ci in conns_info]
        return conns_names


class window(QMainWindow):
    def __init__(self):
        super().__init__()

    def createUI(self):
        self.setGeometry(500, 300, 700, 700)
        self.setWindowTitle("Echo Server")

        self.connection_counter = QtWidgets.QLabel(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.__update_connections)
        self.timer.start(500)

    def closeEvent(self, event):
        close = QtWidgets.QMessageBox.question(self,
            "QUIT",
            "Are you sure want to stop process?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QMessageBox.Yes:
            self.timer.stop()
            shutdown_event.set()
            server.join()
            event.accept()
        else:
            event.ignore()

    def __update_connections(self):
        server.sel.get_map
        self.connection_counter.setText('Current number of connections: ' + str(server.current_connections()))
        self.connection_counter.adjustSize()

shutdown_event = threading.Event()
server = server_thread(HOST, PORT)
server.start()

gui = QApplication(sys.argv)
window = window()
window.createUI()
window.show()
sys.exit(gui.exec_())
