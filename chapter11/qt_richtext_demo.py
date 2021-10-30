from typing import Union, Callable
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtBoundSignal, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextBrowser


SIGNAL = Union[pyqtSignal, pyqtBoundSignal]
SLOT = Union[Callable[..., None], pyqtBoundSignal]


class MainWindow(QMainWindow):
    def __init__(self, *args, width: int = 800, height: int = 600, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.resize(width, height)
        main = QTextBrowser()
        self.setCentralWidget(main)
        main.setOpenExternalLinks(True)
        main.document().setDefaultStyleSheet(
            "body {color: #333; font.size: 14px}"
            "h2 {background: #CCF; color: #443}"
            "h1 {background: #001133}"
        )
        with open("chapter11/fight_fighter2.html", "r") as fh:
            main.insertHtml(fh.read())
        main.setStyleSheet("background-color: #EEF;")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
