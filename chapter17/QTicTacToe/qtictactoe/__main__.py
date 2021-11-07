import sys
from PyQt6.QtWidgets import QApplication
from .mainwindow import MainWindow


def main():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)


if __name__ == "__main__":
    main()
