from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__(parent=None, windowTitle="Fight Fighter Game Lobby")

        # Setup central widget: #
        heading = QLabel("Fight Fighter!")
        inputs: dict[str, QWidget] = {
            "Server": QLineEdit(),
            "Name": QLineEdit(),
            "Password": QLineEdit(echoMode=QLineEdit.EchoMode.Password),
            "Team": QComboBox(),
            "Ready": QCheckBox("Check when ready"),
        }
        teams = ("Crimson Sharks", "Shadow Hawks", "Night Terrors", "Blue Crew")
        inputs["Team"].addItems(teams)
        self.submit = QPushButton(
            "Connect",
            clicked=lambda: QMessageBox.information(
                self, "Connecting", "Prepare for Battle!"
            ),
        )
        self.reset = QPushButton(text="Cancel", clicked=self.close)
        layout = QFormLayout()
        layout.addRow(heading)
        for label, widget in inputs.items():
            layout.addRow(label, widget)
        layout.addRow(self.submit, self.reset)
        cx_form = QWidget()
        cx_form.setLayout(layout)
        self.setCentralWidget(cx_form)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
