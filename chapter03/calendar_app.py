from typing import Any, Optional
from dataclasses import dataclass
from functools import total_ordering
from PyQt6 import QtGui as qtg, QtCore as qtc, QtWidgets as qtw


@dataclass
@total_ordering
class Event:
    title: str
    time: Optional[qtc.QTime]
    category: str
    detail: str = ""

    def __lt__(self, other: Any):
        """Compare Events based on time. All-day events will be treated as '00:00'."""
        if not isinstance(other, Event):
            raise TypeError(
                f"Comparison between {self.__class__.__qualname__} and "
                f"{other.__class__.__qualname__} is not supported."
            )
        return (self.time or qtc.QTime(0, 0)) < (other.time or qtc.QTime(0, 0))


class MainWindow(qtw.QWidget):
    """Calendar app main window"""

    events: dict[qtc.QDate, list[Event]] = {}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        #############################
        # Top level window settings #
        #############################

        self.setWindowTitle("My Calendar App")
        self.resize(800, 600)

        ########################
        # Construct subwidgets #
        ########################

        # Presets:
        EXPANDING = qtw.QSizePolicy(
            qtw.QSizePolicy.Policy.Expanding, qtw.QSizePolicy.Policy.Expanding
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
        self.allday_check = qtw.QCheckBox("All Day")
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

        #################################
        # Connect signals and callbacks #
        #################################

        # disable time entry when 'All Day' is checked:
        self.allday_check.toggled.connect(self.event_time.setDisabled)
        # populate event list on date selection:
        self.calendar.selectionChanged.connect(self.populate_list)
        # populate event details on event selection:
        self.event_list.itemSelectionChanged.connect(self.populate_form)
        # update event list on 'Add/Update':
        self.add_button.clicked.connect(self.save_event)
        # delete selected event on 'Delete':
        self.del_button.clicked.connect(self.delete_event)
        # set 'Delete' button state based on item selection:
        self.event_list.itemSelectionChanged.connect(self.check_delete_btn)
        self.check_delete_btn()

    def clear_form(self):
        self.event_title.clear()
        self.event_category.setCurrentIndex(0)
        self.event_time.setTime(qtc.QTime(8, 0))
        self.allday_check.setChecked(False)
        self.event_detail.setPlainText("")

    def populate_list(self):
        """Populates the event list with events for the currently selected day."""
        self.event_list.setCurrentRow(-1)
        self.event_list.clear()
        self.clear_form()
        date = self.calendar.selectedDate()
        for event in self.events.get(date, []):
            time = event.time.toString(r"hh:mm") if event.time else "All Day"
            self.event_list.addItem(f"{time}: {event.title}")

    def populate_form(self):
        """Populates the event info form with data for the selected event in the event
        list."""
        self.clear_form()
        date = self.calendar.selectedDate()
        event_number = self.event_list.currentRow()
        if event_number == -1:
            return
        event_data = self.events.get(date)[event_number]
        if event_data.time is None:
            self.allday_check.setChecked(True)
        else:
            self.event_time.setTime(event_data.time)
        self.event_title.setText(event_data.title)
        self.event_detail.setText(event_data.detail)

    def save_event(self):
        """Save the data in the event form as a new event or update an existing event."""
        event = Event(
            title=self.event_title.text(),
            category=self.event_category.currentText(),
            time=None if self.allday_check.isChecked() else self.event_time.time(),
            detail=self.event_detail.toPlainText(),
        )
        date = self.calendar.selectedDate()
        event_list = self.events.get(date, [])
        event_number = self.event_list.currentRow()
        if event_number == -1:
            event_list.append(event)
        else:
            event_list[event_number] = event
        event_list.sort()
        self.events[date] = event_list
        self.populate_list()

    def delete_event(self):
        """Delete selected event from the list."""
        date = self.calendar.selectedDate()
        row = self.event_list.currentRow()
        del self.events[date][row]
        self.event_list.setCurrentRow(-1)
        self.clear_form()
        self.populate_list()

    def check_delete_btn(self):
        """Disable 'Delete' when no event is selected."""
        self.del_button.setDisabled(self.event_list.currentRow() == -1)


def main(*args, **kwargs) -> int:
    app = qtw.QApplication(*args, **kwargs)
    mw = MainWindow()
    mw.show()
    return app.exec()


if __name__ == "__main__":
    import sys

    main_rv = main(sys.argv)
    sys.exit(main_rv)
