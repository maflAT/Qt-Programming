from PySide6 import QtGui as qtg
from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw


class IPv4Validator(qtg.QValidator):
    """Enforce entry of an IPv4 Address"""

    def validate(self, proposed: str, index: int) -> qtg.QValidator.State:
        # sourcery skip: convert-any-to-in
        octets = proposed.split(".")
        if len(octets) > 4 or any(len(x) > 3 for x in octets):
            return qtg.QValidator.Invalid
        if not all(x.isdigit() for x in octets if x != ""):
            return qtg.QValidator.Invalid
        if not all(0 <= int(x) <= 255 for x in octets if x != ""):
            return qtg.QValidator.Invalid
        if len(octets) < 4 or any(x == "" for x in octets):
            return qtg.QValidator.Intermediate
        return qtg.QValidator.Acceptable


class ChoiceSpinBox(qtw.QSpinBox):
    """A spinbox for selecting choices."""

    def __init__(self, choices: list[str], *args, **kwargs) -> None:
        self.choices = choices
        super().__init__(*args, maximum=len(self.choices) - 1, minimum=0, **kwargs)

    def valueFromText(self, text: str) -> int:
        """Overrides QSpinBox. Returns list index of the selected text item."""
        return self.choices.index(text)

    def textFromValue(self, value: int) -> str:
        """Overrides QSpinBox. Returns display text for the selected list item."""
        try:
            return self.choices[value]
        except IndexError:
            return "Error!"

    def validate(self, input: str, pos: int) -> qtg.QValidator.State:
        if input in self.choices:
            return qtg.QValidator.Acceptable
        if any(value.startswith(input) for value in self.choices):
            return qtg.QValidator.Intermediate
        return qtg.QValidator.Invalid


class MainWindow(qtw.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        #####################
        # Construct Widgets #
        #####################

        label = qtw.QLabel("Hello Label", self)
        line_edit = qtw.QLineEdit(
            "default value",
            self,
            placeholderText="Type here",
            clearButtonEnabled=True,
            maxLength=20,
            minimumWidth=200,
            maximumSize=qtc.QSize(500, 50),
        )
        line_edit.setText("0.0.0.0")
        line_edit.setValidator(IPv4Validator())
        button = qtw.QPushButton(
            "Push Me",
            self,
            checkable=False,
            checked=True,
            shortcut=qtg.QKeySequence(qtc.Qt.CTRL + qtc.Qt.Key_P),
        )
        combobox = qtw.QComboBox(
            self,
            editable=True,
            insertPolicy=qtw.QComboBox.InsertAtTop,
        )
        combobox.addItem("lemon", 1),
        combobox.addItem("Peach", "Ohh I like Peaches!"),
        combobox.addItem("Strawberry", qtw.QWidget),
        combobox.insertItem(1, "Radish", 2),
        spinbox = qtw.QSpinBox(
            self,
            value=12,
            maximum=100,
            minimum=10,
            prefix="$",
            suffix=" + Tax",
            singleStep=5,
            sizePolicy=qtw.QSizePolicy(
                qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Preferred
            ),
        )
        datetimebox = qtw.QDateTimeEdit(
            self,
            date=qtc.QDate.currentDate(),
            time=qtc.QTime(12, 30),
            calendarPopup=True,
            maximumDate=qtc.QDate(2030, 1, 1),
            maximumTime=qtc.QTime(17, 0),
            displayFormat="yyyy-MM-dd HH:mm",
        )
        textedit = qtw.QTextEdit(
            self,
            acceptRichText=False,
            lineWrapMode=qtw.QTextEdit.FixedColumnWidth,
            lineWrapColumnOrWidth=25,
            placeholderText="your name here",
            sizePolicy=qtw.QSizePolicy(
                qtw.QSizePolicy.MinimumExpanding, qtw.QSizePolicy.MinimumExpanding
            ),
        )
        textedit.sizeHint = lambda: qtc.QSize(500, 200)
        ratingbox = ChoiceSpinBox(choices=["bad", "average", "good", "awesome"])

        #################################
        # Placing and arranging Widgets #
        #################################

        sublayout = qtw.QHBoxLayout()
        sublayout.addWidget(button)
        sublayout.addWidget(combobox)
        sublayout.addWidget(ratingbox)
        form_layout = qtw.QFormLayout()
        form_layout.addRow("Item 1", qtw.QLineEdit())
        form_layout.addRow("Item 2", qtw.QLineEdit())
        form_layout.addRow(qtw.QLabel("<b>This is a label-only row</b>"))
        stretch_layout = qtw.QHBoxLayout()
        stretch_layout.addWidget(qtw.QLineEdit("short"), stretch=1)
        stretch_layout.addWidget(qtw.QLineEdit("long"), stretch=2)
        layout = qtw.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.addLayout(sublayout)
        # layout.addLayout(grid_layout)
        layout.addLayout(form_layout)
        layout.addLayout(stretch_layout)
        self.setLayout(layout)

        #####################
        # Container Widgets #
        #####################

        grid_layout = qtw.QGridLayout()
        grid_layout.addWidget(spinbox, 0, 0)
        grid_layout.addWidget(datetimebox, 0, 1)
        grid_layout.addWidget(textedit, 1, 0, 2, 2)
        container = qtw.QWidget(self)
        container.setLayout(grid_layout)
        tab_widget = qtw.QTabWidget(
            self,
            movable=True,
            tabPosition=qtw.QTabWidget.West,
            tabShape=qtw.QTabWidget.Triangular,
        )
        tab_widget.addTab(container, "Tab the first")
        # tab_widget.addTab(subwidget, "Tab the second")
        layout.addWidget(tab_widget)

        groupbox = qtw.QGroupBox(
            "Buttons",
            checkable=True,
            checked=True,
            alignment=qtc.Qt.AlignHCenter,
            flat=True,
        )
        groupbox.setLayout(qtw.QHBoxLayout())
        groupbox.layout().addWidget(qtw.QPushButton("OK")),
        groupbox.layout().addWidget(qtw.QPushButton("Cancel")),
        layout.addWidget(groupbox)


def main(*args, **kwargs) -> int:
    app = qtw.QApplication(*args, **kwargs)
    mw = MainWindow()
    mw.show()
    return app.exec()


if __name__ == "__main__":
    import sys

    main_rv = main(sys.argv)
    sys.exit(main_rv)
