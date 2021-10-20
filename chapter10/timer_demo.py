from typing import Optional
from PyQt6 import QtWidgets
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


class AutoCloseDialog(QDialog):
    def __init__(
        self, parent: Optional[QWidget], title: str, message: str, timeout: int
    ) -> None:
        super().__init__(parent=parent, windowTitle=title)
        self.setModal(False)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel(message))
        self.timeout = timeout

    def show(self) -> None:
        super().show()
        QTimer.singleShot(self.timeout * 1000, self.hide)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        interval_seconds = 3
        self.timer = QTimer()
        self.timer.setInterval(interval_seconds * 1000)
        self.dialog = AutoCloseDialog(
            self,
            "It's time again",
            f"It has been {interval_seconds} seconds "
            "since this dialog was last shown.",
            2000,
        )
        self.timer.timeout.connect(self.dialog.show)
        self.timer.start()

        toolbar = self.addToolBar("Tools")
        toolbar.addAction("Stop Bugging Me", self.timer.stop)
        toolbar.addAction("Start Bugging Me", self.timer.start)

        self.timer2 = QTimer()
        self.timer2.setInterval(10)
        self.timer2.timeout.connect(self.update_status)
        self.timer2.start()

    def update_status(self):
        if self.timer.isActive():
            time_left = self.timer.remainingTime()
            self.statusBar().showMessage(
                f"Next dialog will be shown in {time_left} milliseconds."
            )
        else:
            self.statusBar().showMessage("Dialogs are off.")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
