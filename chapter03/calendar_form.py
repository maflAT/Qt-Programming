from PySide6 import QtGui as qtg
from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw


class MainWindow(qtw.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setWindowTitle("My Calendar App")
        self.resize(800, 600)

        ########################
        # Construct subwidgets #
        ########################

        # Presets:
        EXPANDING = qtw.QSizePolicy(
            qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding
        )
        EVENT_CATEGORIES = [
            "Select category...",
            "New...",
            "Work",
            "Meeting",
            "Doctor",
            "Family",
        ]
        self.calendar = qtw.QCalendarWidget(sizePolicy=EXPANDING)
        self.event_list = qtw.QListWidget(sizePolicy=EXPANDING)
        self.event_title = qtw.QLineEdit()
        self.event_category = qtw.QComboBox()
        self.event_category.addItems(EVENT_CATEGORIES)
        # disable the first category item since it only serves as placeholder text:
        # model() returns QStandardItemModel which implements `item()`
        self.event_category.model().item(0).setEnabled(False)
        self.event_time = qtw.QTimeEdit(qtc.QTime(8, 0))
        self.allday_check = qtw.QCheckBox("All Cay")
        self.event_detail = qtw.QTextEdit()
        self.add_button = qtw.QPushButton("Add/Update")
        self.del_button = qtw.QPushButton("Delete")

        #####################
        # Layout subwidgets #
        #####################
        event_form_layout = qtw.QGridLayout()
        event_form_layout.addWidget(self.event_title, 1, 1, 1, 3)
        event_form_layout.addWidget(self.event_category, 2, 1)
        event_form_layout.addWidget(self.event_time, 2, 2)
        event_form_layout.addWidget(self.allday_check, 2, 3)
        event_form_layout.addWidget(self.event_detail, 3, 1, 1, 3)
        event_form_layout.addWidget(self.add_button, 4, 2)
        event_form_layout.addWidget(self.del_button, 4, 3)
        event_form = qtw.QGroupBox("Event")
        event_form.setLayout(event_form_layout)
        right_layout = qtw.QVBoxLayout()
        right_layout.addWidget(qtw.QLabel("Events on Date"))
        right_layout.addWidget(self.event_list)
        right_layout.addWidget(event_form)
        main_layout = qtw.QHBoxLayout()
        main_layout.addWidget(self.calendar)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)


def main(*args, **kwargs) -> int:
    app = qtw.QApplication(*args, **kwargs)
    mw = MainWindow()
    mw.show()
    return app.exec()


if __name__ == "__main__":
    import sys

    main_rv = main(sys.argv)
    sys.exit(main_rv)
