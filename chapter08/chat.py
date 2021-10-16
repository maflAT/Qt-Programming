from typing import Optional, Union
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QWidget,
)


class ChatWindow(QWidget):

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
        self.message_view.append(f"<b>{username}: </b>{message}<br>")

    def send(self):
        message = self.message_entry.text().strip()
        if message:
            self.submitted.emit(message)
            self.message_entry.clear()


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget = None, **kwargs) -> None:
        super().__init__(parent=parent, **kwargs)
        self.cw = ChatWindow(self)
        self.setCentralWidget(self.cw)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow(None, windowTitle="Simple-Chat")
    mw.show()
    rv = app.exec()
    sys.exit(rv)
