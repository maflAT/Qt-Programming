from typing import Callable, Optional, Union
from PyQt6.QtGui import QAction
from PyQt6.QtCore import (
    QDir,
    QObject,
    QThread,
    pyqtBoundSignal,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

SIGNAL = Union[pyqtSignal, pyqtBoundSignal]
SLOT = Union[Callable[..., None], pyqtBoundSignal]


class SlowSearcherThread(QThread):
    """Search enging built by subclassing QThread -> THIS IS NOT RECOMMENDED"""

    match_found: SIGNAL = pyqtSignal(str)
    dir_changed: SIGNAL = pyqtSignal(str)
    finished: SIGNAL = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self.term = None

    def set_term(self, term: str):
        self.term = term

    def run(self) -> None:
        root = R"C:\Steam"
        self._search(self.term, root)
        self.finished.emit()

    def _search(self, term: str, path: str):
        self.dir_changed.emit(path)
        directory = QDir(path)
        directory.setFilter(
            directory.filter() | QDir.Filter.NoDotAndDotDot | QDir.Filter.NoSymLinks
        )
        for entry in directory.entryInfoList():
            entry_path = entry.filePath()
            if term in entry_path:
                print(entry_path)
                self.match_found.emit(entry_path)
            if entry.isDir():
                self._search(term, entry_path)


class SearchForm(QWidget):

    textChanged = pyqtSignal(str)
    returnPressed = pyqtSignal()

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self.search_term_inp = QLineEdit(
            placeholderText="Search Term",
            textChanged=self.textChanged,
            returnPressed=self.returnPressed,
        )
        self.results = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.search_term_inp)
        layout.addWidget(self.results)
        self.setLayout(layout)
        self.returnPressed.connect(self.results.clear)

    def addResult(self, result):
        self.results.addItem(result)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # ------------------
        # create search form
        # ------------------

        form = SearchForm()
        self.setCentralWidget(form)

        # --------------------------------
        # create and start a worker thread
        # --------------------------------

        self.ss = SlowSearcherThread()

        # ----------------------------------------------
        # connect front-end (form) and back-end (worker)
        # ----------------------------------------------

        form.textChanged.connect(self.ss.set_term)
        form.returnPressed.connect(self.ss.start)
        self.ss.match_found.connect(form.addResult)
        self.ss.finished.connect(self.on_finished)
        self.ss.dir_changed.connect(self.on_directory_changed)

    def on_finished(self):
        QMessageBox.information(self, "Complete", "Search complete")

    def on_directory_changed(self, path):
        self.statusBar().showMessage(f"Searching in: {path}")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow(windowTitle="SlowSearcher")
    mw.show()
    rv = app.exec()
    sys.exit(rv)
