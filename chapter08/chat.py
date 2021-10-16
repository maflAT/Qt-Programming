from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QWidget,
)


class ChatWindow(QWidget):

    submitted = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.message_view = QTextEdit(readOnly=True)
        self.message_entry = QLineEdit()
        self.send_button = QPushButton("Send", clicked=self.send)
        layout = QGridLayout()
        layout.addWidget(self.message_view, 1, 1, 1, 2)
        layout.addWidget(self.message_entry, 2, 1)
        layout.addWidget(self.send_button, 2, 2)
        self.setLayout(layout)

    def send(self):
        ...


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = ChatWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
