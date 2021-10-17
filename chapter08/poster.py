from typing import Callable, Optional, Union
from PyQt6.QtGui import QAction, QColor, QPalette
from PyQt6.QtCore import QLine, QObject, QUrl, Qt, pyqtBoundSignal, pyqtSignal
from PyQt6.QtNetwork import (
    QHttpMultiPart,
    QHttpPart,
    QNetworkAccessManager,
    QNetworkReply,
    QNetworkRequest,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QSplitterHandle,
    QTableWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

SIGNAL = Union[pyqtSignal, pyqtBoundSignal]
SLOT = Union[Callable[..., None], pyqtBoundSignal]


class Poster(QObject):
    """Backend for http posts."""

    # Emit reply string when
    replyReceived: SIGNAL = pyqtSignal(str)

    requestSent: SIGNAL = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.on_reply)

    def on_reply(self, reply: QNetworkReply):
        reply_bytes = reply.readAll()
        reply_string = bytes(reply_bytes).decode("utf-8")
        self.replyReceived.emit(reply_string)

    def make_request(self, url: QUrl, data: dict[str, str], filename: str):
        """Wrap data into a QHttpMultiPart object and send a post request."""
        self.request = QNetworkRequest(url)
        self.multipart = QHttpMultiPart(QHttpMultiPart.ContentType.FormDataType)
        for k, v in (data or {}).items():
            http_part = QHttpPart()
            http_part.setHeader(
                QNetworkRequest.KnownHeaders.ContentDispositionHeader,
                f'form-data; name="{k}"',
            )
            http_part.setBody(v.encode("utf-8"))
            self.multipart.append(http_part)
        if filename:
            file_part = QHttpPart()
            file_part.setHeader(
                QNetworkRequest.KnownHeaders.ContentDispositionHeader,
                f'form-data; name="attachment"; filename="{filename}"',
            )
            file_data = open(filename, "rb").read()
            file_part.setBody(file_data)
            self.multipart.append(file_part)
        self.manager.post(self.request, self.multipart)
        self.requestSent.emit(f"sent request to {url.url()}")


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(windowTitle="http Poster")
        # init gui elements:
        self.url = QLineEdit()
        self.table = QTableWidget(5, 2)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setHorizontalHeaderLabels(["key", "value"])
        self.fname = QPushButton("(No file)", clicked=self.on_file_btn)
        submit = QPushButton("Submit Post", clicked=self.submit)
        response = QTextEdit(readOnly=True)
        self.status = QLabel()
        self.statusBar().addWidget(self.status)

        # group and arrange elements:
        top_widget = QWidget(minimumWidth=600)
        top_widget.setLayout(QVBoxLayout())
        top_widget.layout().addWidget(self.url)
        top_widget.layout().addWidget(self.table)
        bot_widget = QWidget(minimumWidth=600)
        bot_widget.setLayout(QVBoxLayout())
        for w in (self.fname, submit, response):
            bot_widget.layout().addWidget(w)
        splitter = QSplitter(Qt.Orientation.Vertical, childrenCollapsible=False)
        splitter.addWidget(top_widget)
        splitter.addWidget(bot_widget)
        self.setCentralWidget(splitter)

        # init http backend:
        self.poster = Poster()
        self.poster.requestSent.connect(self.status.setText)
        self.poster.replyReceived.connect(response.setText)

    def on_file_btn(self):
        filename, accepted = QFileDialog.getOpenFileName()
        if accepted:
            self.fname.setText(filename)

    def submit(self):
        url = QUrl(self.url.text())
        filename = self.fname.text()
        if filename == "(No file)":
            filename = None
        data = {}
        for rownum in range(self.table.rowCount()):
            key_item = self.table.item(rownum, 0)
            key = key_item.text() if key_item else None
            if key:
                data[key] = self.table.item(rownum, 1).text()
        self.poster.make_request(url, data, filename)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
