# multiconn-server.py

import sys
import socket
import selectors
import types
import threading
import codecs 
from datetime import datetime
from queue import Queue
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer
from ui.compiled.server_ui import Ui_Server
from ui.compiled.table_model import DictionaryTableModel
from utils.comms import *

# HOST = "127.0.0.1"  # The server's hostname or IP address
# PORT = 65432  # The port used by the server
TIMESTAMP_FORMAT = '%d/%m/%y %H:%M:%S'

class server_thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.ipv4_listening_sock = None
        self.ipv6_listening_sock = None
        self.sel = selectors.DefaultSelector()
        self.user_base = {}
        self.user_groups = {}

    def __accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(
            addr=str(addr), 
            outbound=b"", 
            buffer=Queue(), 
            username="Not authenticated", 
            status="Offline", 
            last_online="Now")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def __service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = recv_msg(sock)  # Should be ready to read
            if recv_data:
                self.__process_segment(recv_data, data)
            else:
                print(f"Closing connection to {data.addr}")
                self.user_base[data.username].status = "Offline"
                data.last_online = datetime.now().strftime(TIMESTAMP_FORMAT)
                self.sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if (data.outbound == b"") and (not data.buffer.empty()):
                data.outbound = data.buffer.get()
            if data.outbound and data.status == "Online":
                print(f"Sending {data.outbound!r} to {data.username}")
                send_msg(sock, data.outbound)
                data.outbound = b""
                # sent = sock.send(data.outbound)  # Should be ready to write
                # data.outbound = data.outbound[sent:]

    def __process_segment(self, segment, user_data):
        message = codecs.decode(segment, "utf-8")
        try:
            (header, metadata, content) = message.split('|')
            match header:
                case "REG":
                    username = content
                    if username in self.user_base.keys():
                        print(f"Welcoming back {username}")
                        last_user_data = self.user_base[username]
                        user_data.outbound = last_user_data.outbound
                        user_data.buffer = last_user_data.buffer
                        user_data.buffer.put(b"SER||you are all caught up")
                    else: 
                        print(f"Registered user {username}")
                    user_data.username = username
                    user_data.status = "Online"
                    self.user_base[username] = user_data
                case "DMS":
                    print(f"Received: {message}")
                    (timestamp, receiver) = metadata.split('#')
                    receiver_data = self.user_base[receiver]
                    message = f"DMS|{timestamp}#{user_data.username}|{content}"
                    receiver_data.buffer.put(codecs.encode(message, "utf-8"))
                case "CUS":
                    timestamp = metadata
                    username = content
                    print(f"Checking status of {username}")
                    if username in self.user_groups.keys():
                        for user in self.user_groups[username]:
                            last_online = self.user_base[user].last_online
                            responce = f"CUS|{timestamp}#{user}#{username}|{last_online}"
                            user_data.buffer.put(codecs.encode(responce, "utf-8"))
                    else:
                        last_online = self.user_base[username].last_online
                        responce = f"CUS|{timestamp}#{username}|{last_online}"
                        user_data.buffer.put(codecs.encode(responce, "utf-8"))
                case "ADG":
                    groupname = metadata
                    members = content.split(',')
                    if groupname not in self.user_groups.keys():
                        print(f"Registering group {groupname} with members {', '.join(members)}")
                        self.user_groups[groupname] = members
                case "GMS":
                    print(f"Received: {message}")
                    (timestamp, groupname) = metadata.split('#')
                    if groupname in self.user_groups.keys():
                        for receiver in self.user_groups[groupname]:
                            receiver_data = self.user_base[receiver]
                            message = f"GMS|{timestamp}#{groupname}#{user_data.username}|{content}"
                            receiver_data.buffer.put(codecs.encode(message, "utf-8"))


        except ValueError:
            print(f"Corrupted message: {message}")


    def start_server(self, host_ipv4, host_ipv6, port):
        self.stop_server()
        print("Starting server...")
        self.ipv4_listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ipv4_listening_sock.bind((host_ipv4, port))
        self.ipv4_listening_sock.listen()
        print(f"Listening on {(host_ipv4, port)}")
        self.ipv4_listening_sock.setblocking(False)
        data = types.SimpleNamespace(addr=(host_ipv4, port), outbound=b"", username="Listening IPv4")
        self.sel.register(self.ipv4_listening_sock, selectors.EVENT_READ, data=data)

        self.ipv6_listening_sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.ipv6_listening_sock.bind((host_ipv6, port))
        self.ipv6_listening_sock.listen()
        print(f"Listening on {(host_ipv6, port)}")
        self.ipv4_listening_sock.setblocking(False)
        data = types.SimpleNamespace(addr=(host_ipv6, port), outbound=b"", username="Listening IPv6")
        self.sel.register(self.ipv6_listening_sock, selectors.EVENT_READ, data=data)

    def stop_server(self):
        if self.ipv4_listening_sock:
            print("Shutting down the IPv4 server...")
            self.sel.unregister(self.ipv4_listening_sock)
            self.ipv4_listening_sock.close()
            self.ipv4_listening_sock = None
        if self.ipv6_listening_sock:
            print("Shutting down the IPv6 server...")
            self.sel.unregister(self.ipv6_listening_sock)
            self.ipv6_listening_sock.close()
            self.ipv6_listening_sock = None

    def run(self):
        while True:
            if shutdown_event.is_set():
                self.stop_server()
                break
            events = self.sel.select(timeout=-1)
            for key, mask in events:
                if key.data.username == "Listening IPv4" or key.data.username == "Listening IPv6":
                    # when data is None, the event came from the listening socket
                    self.__accept_wrapper(key.fileobj)
                else:
                    # when data is defined, the event came from a client socket
                    self.__service_connection(key, mask)

    def current_connections(self):
        conns = self.sel.get_map().values()
        conns_info = [c.data for c in conns]
        conns_names = [ci.username for ci in conns_info]
        return conns_names


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Server()
        self.connection_counter = QtWidgets.QLabel(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.__update_connections)
        self.timer.timeout.connect(self.__render_user_base)
        self.timer.start(500)

    def setup(self):
        self.ui.setupUi(self)
        self.ui.start_button.clicked.connect(lambda: server_process.start_server(
            host_ipv4=self.ui.ipv4_host_input.text(),
            host_ipv6=self.ui.ipv6_host_input.text(),
            port=int(self.ui.port_input.text())
        ))
        self.ui.stop_button.clicked.connect(server_process.stop_server)


    def closeEvent(self, event):
        close = QtWidgets.QMessageBox.question(self,
            "QUIT",
            "Are you sure want to stop process?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QMessageBox.Yes:
            self.timer.stop()
            shutdown_event.set()
            server_process.join()
            event.accept()
        else:
            event.ignore()

    def __update_connections(self):
        server_process.sel.get_map
        self.ui.connection_counter.setText('Current number of connections: ' + str(server_process.current_connections()))
        self.ui.connection_counter.adjustSize()

    def __render_user_base(self):
        entries = []
        for key, value in server_process.user_base.items():
            entry = {'user': key}
            entry.update(vars(value))
            entry.update({'queue_size' : value.buffer.qsize()})
            entries.append(entry)
        headers = ["user", "addr", "status", "last_online", "queue_size"]
        self.ui.user_table.setModel(DictionaryTableModel(entries, headers))
        self.ui.user_table.resizeColumnsToContents()

        


shutdown_event = threading.Event()
server_process = server_thread()
server_process.start()

app = QtWidgets.QApplication(sys.argv)
ui = Window()
ui.setup()
ui.show()
sys.exit(app.exec_())
