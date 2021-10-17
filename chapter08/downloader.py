import sys
from pathlib import Path
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt6.QtCore import QCoreApplication, QObject, QUrl


class Downloader(QObject):
    def __init__(self, url: str) -> None:
        super().__init__()
        self.manager = QNetworkAccessManager(finished=self.on_finished)
        self.request = QNetworkRequest(QUrl(url))
        self.manager.get(self.request)

    def on_finished(self, reply: QNetworkReply):
        """Process result of request"""
        filename = reply.url().fileName() or "download"
        if Path(filename).exists():
            print("file already exists, not overwriting.")
            sys.exit(1)
        with open(filename, "wb") as fh:
            fh.write(reply.readAll())
        print(f"{filename} written")
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <download url>")
        sys.exit(1)
    app = QCoreApplication(sys.argv)
    d = Downloader(sys.argv[1])
    sys.exit(app.exec())
