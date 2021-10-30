from typing import Any, Union, Callable
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QDate, Qt, pyqtBoundSignal, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QWidget,
)


SIGNAL = Union[pyqtSignal, pyqtBoundSignal]
SLOT = Union[Callable[..., None], pyqtBoundSignal]


class InvoiceForm(QWidget):
    submitted = pyqtSignal(dict)

    def __init__(self) -> None:
        super().__init__()
        self.inputs: dict[str, QWidget] = {
            "Customer Name": QLineEdit(),
            "Customer Address": QPlainTextEdit(),
            "Invoice Date": QDateEdit(date=QDate.currentDate(), calendarPopup=True),
            "Days until due": QSpinBox(minimum=0, maximum=60, value=30),
        }
        self.inputs["Customer Address"].setMaximumHeight(75)
        layout = QFormLayout()
        self.setLayout(layout)
        for label, widget in self.inputs.items():
            layout.addRow(label, widget)
        self.line_items = QTableWidget(10, 3)
        self.line_items.setHorizontalHeaderLabels(["Job", "Rate", "Hours"])
        self.line_items.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.line_items.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        layout.addRow(self.line_items)
        for row in range(self.line_items.rowCount()):
            for col in range(self.line_items.columnCount()):
                if col > 0:
                    self.line_items.setCellWidget(row, col, QSpinBox(minimum=0))
        submit = QPushButton("Create Invoice", clicked=self.on_submit)
        layout.addRow(submit)

    def on_submit(self):
        data: dict[str, Any] = {
            "c_name": self.inputs["Customer Name"].text(),
            "c_addr": self.inputs["Customer Address"].toPlainText(),
            "i_date": self.inputs["Invoice Date"].date().toString(),
            "i_due": self.inputs["Invoice Date"]
            .date()
            .addDays(self.inputs["Days until due"].value())
            .toString(),
            "i_terms": f"{self.inputs['Days until due'].value()} days",
        }
        data["line_items"] = []
        for row in range(self.line_items.rowCount()):
            if not self.line_items.item(row, 0):
                continue
            job = self.line_items.item(row, 0).text()
            rate = self.line_items.cellWidget(row, 1).value()
            hours = self.line_items.cellWidget(row, 2).value()
            total = rate * hours
            row_data = [job, rate, hours, total]
            if any(row_data):
                data["line_items"].append(row_data)
        data["total_due"] = sum(x[3] for x in data["line_items"])
        self.submitted.emit(data)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        main = QWidget()
        main.setLayout(QHBoxLayout())
        self.setCentralWidget(main)

        form = InvoiceForm()
        main.layout().addWidget(form)

        # self.preview=InvoiceView()
        # main.layout().addWidget(self.preview)

        # form.submitted.connect(self.preview.build_invoice)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
