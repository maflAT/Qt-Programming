from PyQt6.QtGui import QAction, QFont, QFontInfo, QPixmap
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

        #########################
        # Setup central widget: #
        #########################

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
        self.cancel = QPushButton(text="Cancel", clicked=self.close)
        layout = QFormLayout()
        layout.addRow(heading)
        for label, widget in inputs.items():
            layout.addRow(label, widget)
        layout.addRow(self.submit, self.cancel)
        cx_form = QWidget()
        cx_form.setLayout(layout)
        self.setCentralWidget(cx_form)

        # ==========
        # Set fonts:
        # ==========

        heading_font = QFont("Impact", 32, QFont.Weight.Black)
        heading_font.setStretch(QFont.Stretch.Expanded.value)
        heading.setFont(heading_font)

        label_font = QFont()
        label_font.setFamily("Impact")
        label_font.setPointSize(14)
        label_font.setWeight(QFont.Weight.ExtraLight)
        label_font.setStyle(QFont.Style.StyleItalic)
        for inp in inputs.values():
            layout.labelForField(inp).setFont(label_font)

        # ---------------------
        # handle font fallback:
        # ---------------------

        button_font = QFont("noexists")  # set font
        # print(QFontInfo(button_font).family())  # actual used font
        button_font.setStyleHint(QFont.StyleHint.Fantasy)  # fallback settings
        # print(QFontInfo(button_font).family())  # fallback font
        button_font.setStyleStrategy(
            QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.PreferQuality
        )
        self.submit.setFont(button_font)
        self.cancel.setFont(button_font)

        ##############
        # Add Images #
        ##############

        logo = QPixmap("logo.png")
        heading.setPixmap(logo)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
