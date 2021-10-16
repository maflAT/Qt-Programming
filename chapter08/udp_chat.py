from typing import Optional, Union
from PySide6.QtGui import QAction
from PySide6.QtCore import QByteArray, QDir, QObject, Qt, Signal, SignalInstance
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QWidget,
)
from PySide6.QtNetwork import QAbstractSocket, QHostAddress, QUdpSocket


class UdpChatInterface(QObject):
    """Facilitates communication over UDP."""

    port = 7777
    delimiter = "||"
    received: Union[Signal, SignalInstance] = Signal(str, str)
    error: Union[Signal, SignalInstance] = Signal(str)

    def __init__(self, username: str) -> None:
        super().__init__()
        self.username = username

        self.socket = QUdpSocket()
        self.socket.bind(QHostAddress.Any, self.port)
        self.socket.readyRead.connect(self.process_datagrams)
        self.socket.errorOccurred.connect(self.on_error)

    def on_error(self, socket_error: QAbstractSocket.SocketError):
        # PyQt hack:
        # error_index = QAbstractSocket.staticMetaObject.indexOfEnumerator("SocketError")
        # error = QAbstractSocket.staticMetaObject.enumerator(error_index).valueToKey(
        #     socket_error
        # )
        error = socket_error.value  # does that work???
        message = f"There was a network error: {error}"
        self.error.emit(message)

    def process_datagrams(self):
        """Parses datagrams from the socket and emits a signal with decoded message."""
        while self.socket.hasPendingDatagrams():
            datagram = self.socket.receiveDatagram()
            raw_message = bytes(datagram.data()).decode("utf-8")
            if self.delimiter not in raw_message:
                continue
            username, message = raw_message.split(self.delimiter, 1)
            self.received.emit(username, message)

    def send_message(self, message: str):
        """Encodes a message and writes it to the socket."""
        msg_bytes = f"{self.username}{self.delimiter}{message}".encode("utf-8")
        self.socket.writeDatagram(
            QByteArray(msg_bytes), QHostAddress.Broadcast, self.port
        )


class ChatWindow(QWidget):
    """A widget to send messages and display received messages"""

    submitted: Union[Signal, SignalInstance] = Signal(str)

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self.message_view = QTextEdit(readOnly=True)
        self.message_entry = QLineEdit()
        self.send_button = QPushButton("Send", clicked=self.send)
        layout = QGridLayout()
        layout.addWidget(self.message_view, 1, 1, 1, 2)
        layout.addWidget(self.message_entry, 2, 1)
        layout.addWidget(self.send_button, 2, 2)
        self.setLayout(layout)

    def write_message(self, username: str, message: str):
        """Displays received message in the text box."""
        self.message_view.append(f"<b>{username}: </b>{message}<br>")

    def send(self):
        """Emits a signal with our message."""
        message = self.message_entry.text().strip()
        if message:
            self.submitted.emit(message)
            self.message_entry.clear()


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget = None, **kwargs) -> None:
        super().__init__(parent=parent, **kwargs)
        self.cw = ChatWindow(self)
        self.setCentralWidget(self.cw)
        username = QDir.home().dirName()
        self.interface = UdpChatInterface(username)
        self.cw.submitted.connect(self.interface.send_message)
        self.interface.received.connect(self.cw.write_message)
        self.interface.error.connect(lambda x: QMessageBox.critical(self, "Error", x))


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow(None, windowTitle="Simple-Chat")
    mw.show()
    rv = app.exec()
    sys.exit(rv)
