from typing import Any, Union, Callable
from PyQt6.QtGui import (
    QFont,
    QPageLayout,
    QPageSize,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextFrameFormat,
    QTextImageFormat,
    QTextLength,
    QTextListFormat,
    QTextTableFormat,
)
from PyQt6.QtCore import (
    QDate,
    QDir,
    QRect,
    QRectF,
    QSize,
    QSizeF,
    Qt,
    pyqtBoundSignal,
    pyqtSignal,
)
from PyQt6.QtWidgets import (
    QApplication,
    QDateEdit,
    QFileDialog,
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
    QTextEdit,
    QWidget,
)
from PyQt6.QtPrintSupport import (
    QPageSetupDialog,
    QPrintDialog,
    QPrintPreviewDialog,
    QPrinter,
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


class InvoiceView(QTextEdit):
    dpi: int = 72
    doc_width = int(8.5 * dpi)
    doc_height = int(11 * dpi)

    def __init__(self):
        super().__init__(readOnly=True)
        self.setFixedSize(QSize(self.doc_width, self.doc_height))

    def build_invoice(self, data: dict[str, Any]):
        document = QTextDocument()
        self.setDocument(document)
        document.setPageSize(QSizeF(self.doc_width, self.doc_height))

        cursor = QTextCursor(document)
        cursor.insertText("Invoice, woohoo!")

        # ----------------------------------
        # create frames to hold our content
        # ----------------------------------

        root = document.rootFrame()
        cursor.setPosition(root.lastPosition())

        # Every frame has an associated format.
        # A format must be configured BEFORE it is asigned to a frame.

        logo_frame_fmt = QTextFrameFormat()
        logo_frame_fmt.setBorder(2)
        logo_frame_fmt.setPadding(10)
        logo_frame = cursor.insertFrame(logo_frame_fmt)

        cursor.setPosition(root.lastPosition())
        cust_addr_frame_fmt = QTextFrameFormat()
        cust_addr_frame_fmt.setWidth(self.doc_width * 0.3)
        cust_addr_frame_fmt.setPosition(QTextFrameFormat.Position.FloatRight)
        cust_addr_frame = cursor.insertFrame(cust_addr_frame_fmt)

        cursor.setPosition(root.lastPosition())
        terms_frame_fmt = QTextFrameFormat()
        terms_frame_fmt.setWidth(self.doc_width * 0.5)
        terms_frame_fmt.setPosition(QTextFrameFormat.Position.FloatLeft)
        terms_frame = cursor.insertFrame(terms_frame_fmt)

        cursor.setPosition(root.lastPosition())
        line_items_frame_fmt = QTextFrameFormat()
        line_items_frame_fmt.setMargin(25)
        line_items_frame = cursor.insertFrame(line_items_frame_fmt)

        std_format = QTextCharFormat()

        logo_format = QTextCharFormat()
        logo_format.setFont(QFont("Impact", 24, QFont.Weight.DemiBold))
        logo_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)
        logo_format.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignMiddle)

        label_format = QTextCharFormat()
        label_format.setFont(QFont("Sans", 12, QFont.Weight.Bold))

        # --------------------------
        # Add content to the frames
        # --------------------------

        cursor.setPosition(logo_frame.firstPosition())
        # cursor.insertImage("chapter11/nc_logo.png")

        logo_image_fmt = QTextImageFormat()
        logo_image_fmt.setName("chapter11/nc_logo.png")
        logo_image_fmt.setHeight(48)
        cursor.insertImage(logo_image_fmt, QTextFrameFormat.Position.FloatLeft)
        cursor.insertText("    ")
        cursor.insertText("Ninja Coders, LLC", logo_format)
        cursor.insertBlock()
        cursor.insertText("123 N Wizard St, Yonkers NY 10701", std_format)

        cursor.setPosition(cust_addr_frame.lastPosition())
        address_format = QTextBlockFormat()
        address_format.setAlignment(Qt.AlignmentFlag.AlignRight)
        address_format.setRightMargin(25)
        address_format.setLineHeight(
            150,
            # QTextBlockFormat.LineHeightTypes.ProportionalHeight, # bugged in PyQt6
            1,
        )
        cursor.insertBlock(address_format)
        cursor.insertText("Customer:", label_format)
        cursor.insertBlock(address_format)
        cursor.insertText(data["c_name"], std_format)
        cursor.insertBlock(address_format)
        cursor.insertText(data["c_addr"])

        cursor.setPosition(terms_frame.lastPosition())
        cursor.insertText("Terms:", label_format)
        cursor.insertList(QTextListFormat.Style.ListDisc)

        term_items = (
            f'<b>Invoice dated:</b> {data["i_date"]}',
            f'<b>Invoice terms:</b> {data["i_terms"]}',
            f'<b>Invoice due:</b> {data["i_due"]}',
        )
        for i, item in enumerate(term_items):
            if i > 0:
                cursor.insertBlock()
            cursor.insertHtml(item)

        # ---------------
        # insert a table
        # ---------------

        table_format = QTextTableFormat()
        table_format.setHeaderRowCount(1)
        table_format.setWidth(QTextLength(QTextLength.Type.PercentageLength, 100))
        headings = ("Job", "Rate", "Hours", "Cost")
        num_rows = len(data["line_items"]) + 1
        num_cols = len(headings)

        cursor.setPosition(line_items_frame.lastPosition())
        table = cursor.insertTable(num_rows, num_cols, table_format)
        for heading in headings:
            cursor.insertText(heading, label_format)
            cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        for row in data["line_items"]:
            for col, value in enumerate(row):
                text = f"${value}" if col in (1, 3) else f"{value}"
                cursor.insertText(text, std_format)
                cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        table.appendRows(1)
        cursor = table.cellAt(num_rows, 0).lastCursorPosition()
        cursor.insertText("Total", label_format)
        cursor = table.cellAt(num_rows, 3).lastCursorPosition()
        cursor.insertText(f'${data["total_due"]}', label_format)

    def set_page_size(self, qrect: QRectF):
        self.doc_width = qrect.width()
        self.doc_height = qrect.height()
        self.setFixedSize(int(self.doc_width) + 3, int(self.doc_height) + 3)
        self.document().setPageSize(QSizeF(self.doc_width, self.doc_height))


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        main = QWidget()
        main.setLayout(QHBoxLayout())
        self.setCentralWidget(main)

        form = InvoiceForm()
        main.layout().addWidget(form)

        self.preview = InvoiceView()
        main.layout().addWidget(self.preview)

        form.submitted.connect(self.preview.build_invoice)

        print_tb = self.addToolBar("Printing")
        print_tb.addAction("Configure Printer", self.printer_config)
        print_tb.addAction("Print Preview", self.print_preview)
        print_tb.addAction("Print Dialog", self.print_dialog)
        print_tb.addAction("Export PDF", self.export_pdf)

        self.printer = QPrinter()
        self.printer.setPageOrientation(QPageLayout.Orientation.Portrait)
        self.printer.setPageSize(QPageSize(QPageSize.PageSizeId.Letter))

    ###################
    # Print functions #
    ###################

    def printer_config(self):
        dialog = QPageSetupDialog(self.printer, self)
        dialog.exec()
        self._update_preview_size()

    def _update_preview_size(self):
        self.preview.set_page_size(self.printer.pageRect(QPrinter.Unit.Point))

    def _print_document(self):
        self.preview.document().print(self.printer)

    def print_dialog(self):
        self._print_document()
        dialog = QPrintDialog(self.printer, self)
        dialog.exec()
        self._update_preview_size()

    def print_preview(self):
        dialog = QPrintPreviewDialog(self.printer, self)
        dialog.paintRequested.connect(self._print_document)
        dialog.exec()
        self._update_preview_size()

    def export_pdf(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save to PDF", QDir.homePath(), "PDF Files (*.pdf)"
        )
        if filename:
            self.printer.setOutputFileName(filename)
            self.printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            self._print_document()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
