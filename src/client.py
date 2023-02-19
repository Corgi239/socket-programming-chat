import sys
import socket
import selectors
import types
import codecs 
import threading
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from ui.compiled.client_ui import Ui_Client
from utils.comms import *

# HOST = "127.0.0.1"  # The server's hostname or IP address
# PORT = 65432  # The port used by the server
TIMESTAMP_FORMAT = '%d/%m/%y %H:%M:%S'

class client_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sel = selectors.DefaultSelector()
        self.username = None
        self.sock = None
        self.data = None
        self.chats = {}
        self.groupchats = []

    def start_connection(self, host, port, username, ipv4=True):
        self.close_connection()
        self.username = username
        server_addr = (host, port)
        print(f"Starting connection to {server_addr}")
        if ipv4:
            sock_family = socket.AF_INET
        else:
            sock_family = socket.AF_INET6
        self.sock = socket.socket(sock_family, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            outbound=codecs.encode(f"REG||{username}", "utf-8")
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
            # recv_data = sock.recv(1024)  # Should be ready to read
            recv_data = recv_msg(sock)
            if recv_data:
                self.__process_segment(recv_data)
            if not recv_data:
                self.close_connection()
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outbound:
                print(f"Sending {data.outbound!r} to server")
                # sent = sock.send(data.outbound)  # Should be ready to write
                # data.outbound = data.outbound[sent:]
                send_msg(sock, data.outbound)
                data.outbound = b""
    
    def __process_segment(self, segment):
        message = codecs.decode(segment, "utf-8")
        try:
            (header, metadata, content) = message.split('|')
            match header:
                case "DMS":
                    print(f"Received: {message}")
                    (timestamp, sender) = metadata.split('#')
                    timestamp = datetime.strptime(timestamp, TIMESTAMP_FORMAT)
                    if sender not in self.chats.keys():
                        self.add_contact(sender)
                    self.chats[sender].append((timestamp, sender, content))
                case "CUS":
                    # (timestamp, username) = metadata.split('#')
                    timestamp = metadata.split('#')[0]
                    username = metadata.split('#')[1]
                    timestamp = datetime.strptime(timestamp, TIMESTAMP_FORMAT)
                    if content == "Now":
                        message = f"{username} is currently online"
                    else:
                        message = f"{username} was last online on {content}"
                    if metadata.count('#') > 1:
                        groupname = metadata.split('#')[2]
                        self.chats[groupname].append((timestamp, "server message", message))
                    else:
                        self.chats[username].append((timestamp, "server message", message))
                case "GMS":
                    print(f"Received: {message}")
                    (timestamp, groupname, sender) = metadata.split('#')
                    timestamp = datetime.strptime(timestamp, TIMESTAMP_FORMAT)
                    if groupname not in self.chats.keys():
                        self.add_contact(groupname)
                        self.groupchats.append(groupname)
                    self.chats[groupname].append((timestamp, sender, content))
                case _:
                    print(f"Unknown header: {header}")
        except ValueError:
            print(f"Corrupted message: {message}")

    
    def add_contact(self, username):
        print(f"Adding contact: {username}")
        if username not in self.chats.keys():
            self.chats[username] = []

    def add_group(self, groupname, members):
        print(f"Adding group: {groupname}")
        if self.username not in members:
            members = members + f",{self.username}"
        if groupname not in self.chats.keys():
            self.groupchats.append(groupname)
            self.chats[groupname] = []
            request = f"ADG|{groupname}|{members}"
            self.data.outbound = codecs.encode(request, "utf-8")

    def send_message(self, receiver, msg):
        now = datetime.now().strftime(TIMESTAMP_FORMAT)
        if receiver in self.groupchats:
            self.data.outbound += codecs.encode(f"GMS|{now}#{receiver}|{msg}", "utf-8")
        else:
            self.data.outbound += codecs.encode(f"DMS|{now}#{receiver}|{msg}", "utf-8")
            self.chats[receiver].append((datetime.now(), self.username, msg))

    def check_user_status(self, username):
        now = datetime.now().strftime(TIMESTAMP_FORMAT)
        request = f"CUS|{now}|{username}"
        self.data.outbound = codecs.encode(request, "utf-8")

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

    def __init__(self, username=""):
        super().__init__()
        self.ui = Ui_Client()
        self.username = username
        self.timer = QTimer()
        self.timer.timeout.connect(self.__render_chat_window)
        self.timer.timeout.connect(self.__update_chat_list)
        self.timer.start(200)

    def setup(self):
        self.ui.setupUi(self)
        self.ui.username_input.setText(self.username)
        self.ui.connect_button.clicked.connect(lambda: client_process.start_connection(
            host=self.ui.host_input.text(),
            port=int(self.ui.port_input.text()),
            username=self.ui.username_input.text(),
            ipv4=self.ui.ipv4_radio.isChecked()
        ))
        self.ui.disconnect_button.clicked.connect(client_process.close_connection)
        self.ui.send_button.clicked.connect(lambda: client_process.send_message(
            receiver=self.ui.chat_selection.currentText(),
            msg=self.ui.message_input.toPlainText()
        ))
        for user in client_process.chats.keys():
            self.ui.chat_selection.addItem(user)
        self.ui.add_contact_button.clicked.connect(lambda: self.__add_contact(
            username=self.ui.new_contact_username_input.text()
        ))
        self.ui.chat_selection.currentTextChanged.connect(lambda: self.__render_chat_window)
        self.ui.check_status_button.clicked.connect(lambda: client_process.check_user_status(
            username=self.ui.chat_selection.currentText()
        ))
        self.ui.add_group_button.clicked.connect(lambda: client_process.add_group(
            groupname=self.ui.new_group_name_input.text(),
            members=self.ui.new_group_members.text()
        ))

    def __render_chat_window(self):
        def format_message(message):
            timestamp = message[0].strftime('%H:%M:%S')
            return f"[{timestamp}] {message[1]}: {message[2]}"
        chat_name = chat_name=self.ui.chat_selection.currentText()
        if chat_name in client_process.chats.keys():
            chat = '\n'.join(format_message(e) for e in client_process.chats[chat_name][::-1])
            self.ui.chat_display.setPlainText(chat)

    def __update_chat_list(self):
        client_chat_names = client_process.chats.keys()
        for chat_name in client_chat_names:
            if self.ui.chat_selection.findText(chat_name) == -1:
                self.ui.chat_selection.addItem(chat_name)

    def __add_contact(self, username):
        client_process.add_contact(username)

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
ui = Window(app.arguments()[1])
ui.setup()
ui.show()
sys.exit(app.exec_())