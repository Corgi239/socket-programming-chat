# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/raw/client.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Client(object):
    def setupUi(self, Client):
        Client.setObjectName("Client")
        Client.resize(341, 624)
        self.centralwidget = QtWidgets.QWidget(Client)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 40, 101, 16))
        self.label.setObjectName("label")
        self.host_input = QtWidgets.QLineEdit(self.centralwidget)
        self.host_input.setGeometry(QtCore.QRect(110, 40, 141, 21))
        self.host_input.setObjectName("host_input")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 70, 31, 16))
        self.label_2.setObjectName("label_2")
        self.port_input = QtWidgets.QLineEdit(self.centralwidget)
        self.port_input.setGeometry(QtCore.QRect(110, 70, 51, 21))
        self.port_input.setObjectName("port_input")
        self.connect_button = QtWidgets.QPushButton(self.centralwidget)
        self.connect_button.setGeometry(QtCore.QRect(120, 130, 101, 31))
        self.connect_button.setObjectName("connect_button")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(0, 170, 341, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.ipv4_radio = QtWidgets.QRadioButton(self.centralwidget)
        self.ipv4_radio.setGeometry(QtCore.QRect(280, 40, 51, 20))
        self.ipv4_radio.setChecked(True)
        self.ipv4_radio.setObjectName("ipv4_radio")
        self.ipv6_radio = QtWidgets.QRadioButton(self.centralwidget)
        self.ipv6_radio.setGeometry(QtCore.QRect(280, 70, 51, 20))
        self.ipv6_radio.setObjectName("ipv6_radio")
        self.connection_status = QtWidgets.QLabel(self.centralwidget)
        self.connection_status.setGeometry(QtCore.QRect(10, 130, 91, 31))
        self.connection_status.setObjectName("connection_status")
        self.address_input = QtWidgets.QLineEdit(self.centralwidget)
        self.address_input.setGeometry(QtCore.QRect(110, 220, 141, 21))
        self.address_input.setObjectName("address_input")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(110, 10, 121, 16))
        self.label_4.setTextFormat(QtCore.Qt.MarkdownText)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(110, 190, 121, 16))
        self.label_5.setTextFormat(QtCore.Qt.MarkdownText)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(10, 220, 60, 16))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(10, 100, 71, 16))
        self.label_7.setObjectName("label_7")
        self.username_input = QtWidgets.QLineEdit(self.centralwidget)
        self.username_input.setGeometry(QtCore.QRect(110, 100, 141, 21))
        self.username_input.setObjectName("username_input")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(10, 250, 71, 16))
        self.label_8.setObjectName("label_8")
        self.message_input = QtWidgets.QTextEdit(self.centralwidget)
        self.message_input.setGeometry(QtCore.QRect(110, 250, 211, 41))
        self.message_input.setObjectName("message_input")
        self.send_button = QtWidgets.QPushButton(self.centralwidget)
        self.send_button.setGeometry(QtCore.QRect(220, 300, 101, 32))
        self.send_button.setObjectName("send_button")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(0, 340, 341, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(110, 360, 121, 16))
        self.label_9.setTextFormat(QtCore.Qt.MarkdownText)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.chat_selection = QtWidgets.QComboBox(self.centralwidget)
        self.chat_selection.setGeometry(QtCore.QRect(110, 390, 91, 32))
        self.chat_selection.setObjectName("chat_selection")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(10, 390, 60, 31))
        self.label_10.setObjectName("label_10")
        self.chat_display = QtWidgets.QTextBrowser(self.centralwidget)
        self.chat_display.setGeometry(QtCore.QRect(10, 430, 321, 181))
        self.chat_display.setObjectName("chat_display")
        self.diconnect_button = QtWidgets.QPushButton(self.centralwidget)
        self.diconnect_button.setGeometry(QtCore.QRect(230, 130, 101, 31))
        self.diconnect_button.setObjectName("diconnect_button")
        Client.setCentralWidget(self.centralwidget)

        self.retranslateUi(Client)
        QtCore.QMetaObject.connectSlotsByName(Client)

    def retranslateUi(self, Client):
        _translate = QtCore.QCoreApplication.translate
        Client.setWindowTitle(_translate("Client", "MainWindow"))
        self.label.setText(_translate("Client", "Server address:"))
        self.host_input.setText(_translate("Client", "127.0.0.1"))
        self.label_2.setText(_translate("Client", "Port:"))
        self.port_input.setText(_translate("Client", "65432"))
        self.connect_button.setText(_translate("Client", "Connect"))
        self.ipv4_radio.setText(_translate("Client", "IPv4"))
        self.ipv6_radio.setText(_translate("Client", "IPv6"))
        self.connection_status.setText(_translate("Client", "Status: Offline"))
        self.label_4.setText(_translate("Client", "*Server connection*"))
        self.label_5.setText(_translate("Client", "*Send messages*"))
        self.label_6.setText(_translate("Client", "Send to:"))
        self.label_7.setText(_translate("Client", "Username:"))
        self.username_input.setText(_translate("Client", "Alpha"))
        self.label_8.setText(_translate("Client", "Message:"))
        self.send_button.setText(_translate("Client", "Send"))
        self.label_9.setText(_translate("Client", "*Dialogues*"))
        self.label_10.setText(_translate("Client", "Chat:"))
        self.diconnect_button.setText(_translate("Client", "Disconnect"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Client = QtWidgets.QMainWindow()
    ui = Ui_Client()
    ui.setupUi(Client)
    Client.show()
    sys.exit(app.exec_())
