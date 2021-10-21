from typing import Union, Callable
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtBoundSignal, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QWidget,
)


SIGNAL = Union[pyqtSignal, pyqtBoundSignal]
SLOT = Union[Callable[..., None], pyqtBoundSignal]


class HashForm(QWidget):

    submitted: SIGNAL = pyqtSignal(str, str, int)

    def __init__(self):
        super().__init__()

        # ---------------
        # create widgets:
        # ---------------
        self.source_path = QPushButton(
            "Click to select...", clicked=self.on_source_click
        )
        self.destination_file = QPushButton(
            "Click to select...", clicked=self.on_dest_click
        )
        self.threads = QSpinBox(minimum=1, maximum=7, value=2)
        submit = QPushButton("Go", clicked=self.on_submit)

        # ---------------
        # arrange layout:
        # ---------------
        layout = QFormLayout()
        layout.addRow("Source Path", self.source_path)
        layout.addRow("Destination File", self.destination_file)
        layout.addRow("Threads", self.threads)
        layout.addRow(submit)
        self.setLayout(layout)

    def on_source_click(self):
        path = QFileDialog.getExistingDirectory()
        if path:
            self.source_path.setText(path)

    def on_dest_click(self):
        filename, _ = QFileDialog.getSaveFileName()
        if filename:
            self.destination_file.setText(filename)

    def on_submit(self):
        self.submitted.emit(
            self.source_path.text(),
            self.destination_file.text(),
            self.threads.value(),
        )


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setCentralWidget(HashForm())


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow(windowTitle="hasher")
    mw.show()
    rv = app.exec()
    sys.exit(rv)
