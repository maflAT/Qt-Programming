from typing import AbstractSet, Optional, Union
from PySide6.QtGui import QAction
from PySide6.QtCore import (
    QByteArray,
    QDataStream,
    QDir,
    QObject,
    Qt,
    Signal,
    SignalInstance,
)
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QInputDialog,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QWidget,
)
from PySide6.QtNetwork import (
    QAbstractSocket,
    QHostAddress,
    QTcpServer,
    QTcpSocket,
    QUdpSocket,
)


class TcpChatInterface(QObject):
    """Facilitates communication over TCP."""

    port = 7777
    delimiter = "||"
    received: Union[Signal, SignalInstance] = Signal(str, str)
    error: Union[Signal, SignalInstance] = Signal(str)

    def __init__(self, username: str, recipient: str) -> None:
        super().__init__()
        self.username = username
        self.recipient = recipient

        # ---------------------
        # initialize TCP Server
        # ---------------------

        self.listener = QTcpServer()
        self.listener.listen(QHostAddress.Any, self.port)
        self.listener.acceptError.connect(self.on_error)
        self.listener.newConnection.connect(self.on_connection)
        self.connections: list[QTcpSocket] = []

        # ---------------------
        # initialize TCP client
        # ---------------------

        self.client_socket = QTcpSocket()
        self.client_socket.errorOccurred.connect(self.on_error)

    def on_error(self, socket_error: QAbstractSocket.SocketError):
        # PyQt hack:
        # error_index = QAbstractSocket.staticMetaObject.indexOfEnumerator("SocketError")
        # error = QAbstractSocket.staticMetaObject.enumerator(error_index).valueToKey(
        #     socket_error
        # )
        error = socket_error.value  # does that work???
        message = f"There was a network error: {error}"
        self.error.emit(message)

    def on_connection(self):
        """Handle incoming connections."""
        connection = self.listener.nextPendingConnection()
        connection.readyRead.connect(self.process_datastream)
        self.connections.append(connection)

    def process_datastream(self):
        """Handle incoming data."""
        for socket in self.connections:
            self.datastream = QDataStream(socket)
            if not socket.bytesAvailable():
                continue
            message_len = self.datastream.readUInt32()
            raw_message = self.datastream.readQString()
            if raw_message and self.delimiter in raw_message:
                username, message = raw_message.split(self.delimiter, 1)
                self.received.emit(username, message)

    def send_message(self, message: str):
        """Establishes connection to the server and sends data stream."""
        raw_message = f"{self.username}{self.delimiter}{message}"
        socket_state = self.client_socket.state()
        if socket_state != QAbstractSocket.ConnectedState:
            self.client_socket.connectToHost(self.recipient, self.port)
        self.datastream = QDataStream(self.client_socket)
        self.datastream.writeUInt32(len(raw_message))
        self.datastream.writeQString(raw_message)

        # emit received signal for local display in the text box.
        self.received.emit(self.username, message)


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
        recipient, _ = QInputDialog.getText(
            self, "Recipient", "Specify the IP or hostname of the remote host."
        )
        if not recipient:
            sys.exit()
        self.interface = TcpChatInterface(username, recipient=recipient)
        self.cw.submitted.connect(self.interface.send_message)
        self.interface.received.connect(self.cw.write_message)
        self.interface.error.connect(lambda x: QMessageBox.critical(self, "Error", x))


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow(None, windowTitle="TCP-Chat")
    mw.show()
    rv = app.exec()
    sys.exit(rv)
