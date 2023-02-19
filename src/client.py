import sys
import socket
import selectors
import types
import codecs 
import threading
from PyQt5 import QtWidgets
from ui.compiled.client_ui import Ui_Client

# HOST = "127.0.0.1"  # The server's hostname or IP address
# PORT = 65432  # The port used by the server

class client_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sel = selectors.DefaultSelector()
        self.sock = None
        self.data = None
        self.known_users = []
        self.chats = {}

    def start_connection(self, host, port, username):
        self.close_connection()
        server_addr = (host, port)
        print(f"Starting connection to {server_addr}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            outbound=codecs.encode("REG" + username, "utf-8")
        )
        self.data = data
        self.sel.register(self.sock, events, data=data)

    def close_connection(self):
        if self.sock:
            print("Closing connection with server")
            self.sel.unregister(self.sock)
            self.sock.close()
            self.sock = None

    def __service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                print(f"Received {recv_data!r} from server")
            if not recv_data:
                self.close_connection()
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outbound:
                print(f"Sending {data.outbound!r} to server")
                sent = sock.send(data.outbound)  # Should be ready to write
                data.outbound = data.outbound[sent:]
    
    def __process_segment(self, segment):
        message = codecs.decode(segment, "utf-8")
        if len(message) < 3:
            return
        header = message[:3]
        print(header)
        match header:
            case "MSG":
                self.data.outbound = codecs.encode(message, "utf-8")
    
    def send_message(self, receiver, msg):
        self.data.outbound += codecs.encode("MSG" + msg,"utf-8")

    def run(self):
        while True:
            if shutdown_event.is_set():
                print("Shutting down the client...")
                self.sel.close()
                break
            if not self.sel:
                continue
            else:
                events = self.sel.select(timeout=-1)
                for key, mask in events:
                    self.__service_connection(key, mask)

class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Client()

    def setup(self):
        self.ui.setupUi(self)
        self.ui.connect_button.clicked.connect(lambda: client_process.start_connection(
            host=self.ui.host_input.text(),
            port=int(self.ui.port_input.text()),
            username=self.ui.username_input.text()
        ))
        self.ui.diconnect_button.clicked.connect(client_process.close_connection)
        self.ui.send_button.clicked.connect(lambda: client_process.send_message(
            msg=self.ui.message_input.toPlainText()
        ))

    def closeEvent(self, event):
        # close = QtWidgets.QMessageBox.question(self,
        #     "QUIT",
        #     "Are you sure want to stop process?",
        #     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        # if close == QtWidgets.QMessageBox.Yes:
            shutdown_event.set()
            client_process.join()
            event.accept()
        # else:
        #     event.ignore()

shutdown_event = threading.Event()
client_process = client_thread()
client_process.start()

app = QtWidgets.QApplication(sys.argv)
ui = Window()
ui.setup()
ui.show()
sys.exit(app.exec_())