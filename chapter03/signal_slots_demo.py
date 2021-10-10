from PyQt6 import QtGui as qtg, QtCore as qtc, QtWidgets as qtw


class FormWindow(qtw.QWidget):
    # submitted = qtc.Signal(str)  # PySide implementation
    submitted = qtc.pyqtSignal([str], [int, str])  # PyQt implementation

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setLayout(qtw.QVBoxLayout())
        self.edit = qtw.QLineEdit()
        self.submit = qtw.QPushButton("Submit", clicked=self.onSubmit)
        self.layout().addWidget(self.edit)
        self.layout().addWidget(self.submit)

    def onSubmit(self):
        text = self.edit.text()
        if text.isdigit():
            self.submitted[int, str].emit(int(text), text)
        else:
            self.submitted[str].emit(text)
        self.close()


class MainWindow(qtw.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setLayout(qtw.QVBoxLayout())
        self.label = qtw.QLabel("click 'Change' to change this text.")
        self.change = qtw.QPushButton("Change", clicked=self.onChange)
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.change)

    # @qtc.pyqtSlot(str)  # PyQt implementation
    def onSubmittedStr(self, string):
        self.label.setText(string)

    # @qtc.pyqtSlot(int, str)  # PyQt implementation
    def onSubmittedIntStr(self, integer, string):
        text = f"The string {string} becomes the number {integer}"
        self.label.setText(text)

    # @qtc.Slot() # PySide implementation
    def onChange(self):
        self.formwindow = FormWindow()
        self.formwindow.submitted[str].connect(
            self.onSubmittedStr
        )  # PyQt implementation
        self.formwindow.submitted[int, str].connect(
            self.onSubmittedIntStr
        )  # PyQt implementation
        self.formwindow.show()


def main(*args, **kwargs) -> int:
    app = qtw.QApplication(*args, **kwargs)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    import sys

    main_rv = main(sys.argv)
    sys.exit(main_rv)
