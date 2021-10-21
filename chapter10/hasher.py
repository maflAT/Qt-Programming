from typing import Union, Callable
from PyQt6.QtGui import QAction
from PyQt6.QtCore import (
    QCryptographicHash,
    QDir,
    QMutex,
    QMutexLocker,
    QObject,
    QRunnable,
    QThread,
    QThreadPool,
    Qt,
    pyqtBoundSignal,
    pyqtSignal,
    pyqtSlot,
)
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


class HashManager(QObject):
    """Receives a list of files to be hashed from the `HashForm` and assigns each file
    to a `HashRunner`."""

    finished: SIGNAL = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.pool = QThreadPool.globalInstance()

    @pyqtSlot(str, str, int)
    def do_hashing(self, source: str, destination: str, threads: int):
        self.pool.setMaxThreadCount(threads)
        qdir = QDir(source)
        for filename in qdir.entryList(QDir.Filter.Files):
            filepath = qdir.absoluteFilePath(filename)
            runner = HashRunner(filepath, destination)
            self.pool.start(runner)
        self.pool.waitForDone()
        self.finished.emit()


class HashRunner(QRunnable):
    """Worker thread for hashing a file and writing the result to another file."""

    file_lock = QMutex()

    def __init__(self, infile: str, outfile: str) -> None:
        super().__init__()
        self.infile = infile
        self.outfile = outfile
        self.hasher = QCryptographicHash(QCryptographicHash.Algorithm.Md5)
        self.setAutoDelete(True)

    def run(self) -> None:
        """This is our main method. It is called by `QThreadPool.start()`."""
        print(f"hashing {self.infile}...")
        self.hasher.reset()
        with open(self.infile, "rb") as fh:
            self.hasher.addData(fh.read())
        hash_string = bytes(self.hasher.result().toHex()).decode("utf-8")

        # ----------------------------------------
        # traditional approach using try / finally
        # ----------------------------------------
        # try:
        #     self.file_lock.lock()
        #     with open(self.outfile, "a", encoding="utf-8") as out:
        #         out.write(f"{self.infile}\t{hash_string}\n")
        # finally:
        #     self.file_lock.unlock()

        # -----------------------------------------------
        # alternative, using QMutexLocker context manager
        # -----------------------------------------------
        with QMutexLocker(self.file_lock):
            with open(self.outfile, "a", encoding="utf-8") as out:
                out.write(f"{self.infile}\t{hash_string}\n")


class HashForm(QWidget):
    """Front end for selecting a directory and configuring settings of the hash runner."""

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
        form = HashForm()
        self.setCentralWidget(form)

        self.manager = HashManager()
        self.manager_thread = QThread()
        self.manager.moveToThread(self.manager_thread)
        self.manager_thread.start()
        form.submitted.connect(self.manager.do_hashing)
        form.submitted.connect(
            lambda x, y, z: self.statusBar().showMessage(
                f"Processing files in {x} into {y} with {z} threads."
            )
        )
        self.manager.finished.connect(lambda: self.statusBar().showMessage("Finished"))


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow(windowTitle="hasher")
    mw.show()
    rv = app.exec()
    sys.exit(rv)
