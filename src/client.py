import sys
import socket
import selectors
import types
import codecs 
import threading
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

class client_thread(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.sel = selectors.DefaultSelector()
        self.message = b"Message from client."
        self.data = None

    def __start_connection(self, host, port):
        server_addr = (host, port)
        print(f"Starting connection to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            outbound=self.message,
        )
        self.data = data
        self.sel.register(sock, events, data=data)

    def __service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                print(f"Received {recv_data!r} from server")
            if not recv_data:
                print(f"Closing connection with server")
                self.sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outbound:
                print(f"Sending {data.outbound!r} to server")
                sent = sock.send(data.outbound)  # Should be ready to write
                data.outbound = data.outbound[sent:]
    
    def send_message(self, msg):
        self.data.outbound += codecs.encode(msg,"utf-8")

    def run(self):
        self.__start_connection(HOST, PORT)
        while True:
            if shutdown_event.is_set():
                print("Shutting down the client...")
                self.sel.close()
                break
            events = self.sel.select(timeout=-1)
            for key, mask in events:
                self.__service_connection(key, mask)

class window(QMainWindow):
    def __init__(self):
        super().__init__()

    def createUI(self):
        self.setGeometry(500, 300, 700, 700)
        self.setWindowTitle("Echo Client")

        self.msg_box = QtWidgets.QLineEdit(self)
        self.send_button = QtWidgets.QPushButton(self)
        self.send_button.setText("Send")
        self.send_button.move(0,50)
        self.send_button.clicked.connect(lambda: self.send_message(self.msg_box.text()))
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.__update_connections)
        # self.timer.start(500)

    def send_message(self, msg):
        client.send_message(msg)

    def closeEvent(self, event):
        close = QtWidgets.QMessageBox.question(self,
            "QUIT",
            "Are you sure want to stop process?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QMessageBox.Yes:
            shutdown_event.set()
            client.join()
            event.accept()
        else:
            event.ignore()


shutdown_event = threading.Event()
client = client_thread(HOST, PORT)
client.start()

gui = QApplication(sys.argv)
window = window()
window.createUI()
window.show()
sys.exit(gui.exec_())