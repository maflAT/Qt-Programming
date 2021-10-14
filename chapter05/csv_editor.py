from typing import Any
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6 import QtWidgets as qtw
import csv


class CsvTableModel(QAbstractTableModel):
    """The model for our csv table."""

    def __init__(self, csv_file: str) -> None:
        super().__init__()
        self.filename = csv_file
        with open(self.filename) as fh:
            reader = csv.reader(fh)
            self._headers = next(reader)
            self._data = list(reader)

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = None) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> Any:
        if role in (Qt.ItemDataRole.EditRole, Qt.ItemDataRole.DisplayRole):
            return self._data[index.row()][index.column()]

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return self._headers[section]
        else:
            return super().headerData(section, orientation, role=role)

    def sort(
        self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder
    ) -> None:
        self.layoutAboutToBeChanged.emit()
        self._data.sort(
            key=lambda x: x[column],
            reverse=(order == Qt.SortOrder.DescendingOrder),
        )
        self.layoutChanged.emit()

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        else:
            return False

    def insertRows(self, row: int, count: int, parent: QModelIndex = None) -> bool:
        self.beginInsertRows(parent or QModelIndex(), row, row + count - 1)
        for _ in range(count):
            default_row = [""] * len(self._headers)
            self._data.insert(row, default_row)
        self.endInsertRows()

    def removeRows(self, row: int, count: int, parent: QModelIndex = None) -> bool:
        self.beginRemoveRows(parent or QModelIndex(), row, row + count - 1)
        for _ in range(count):
            del self._data[row]
        self.endRemoveRows()

    def save_data(self):
        with open(self.filename, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(self._headers)
            writer.writerows(self._data)


class MainWindow(qtw.QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tableview = qtw.QTableView()
        self.tableview.setSortingEnabled(True)
        self.setCentralWidget(self.tableview)

        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        file_menu.addAction("Open", self.select_file)
        file_menu.addAction("Save", self.save_file)

        edit_menu = menu.addMenu("Edit")
        edit_menu.addAction("Insert Above", self.insert_above)
        edit_menu.addAction("Insert Below", self.insert_below)
        edit_menu.addAction("Remove Rows", self.remove_rows)

    def select_file(self):
        filename, _ = qtw.QFileDialog.getOpenFileName(
            parent=self,
            caption="Select CSV file to open...",
            filter="CSV Files (*.csv)  ;; All Files (*)",
        )
        if filename:
            self.model = CsvTableModel(filename)
            self.tableview.setModel(self.model)

    def save_file(self):
        if self.model:
            self.model.save_data()

    def insert_above(self):
        selected = self.tableview.selectedIndexes()
        row = selected[0].row() if selected else 0
        self.model.insertRows(row=row, count=1, parent=None)

    def insert_below(self):
        selected = self.tableview.selectedIndexes()
        row = selected[-1].row() if selected else self.model.rowCount(parent=None)
        self.model.insertRows(row=row + 1, count=1, parent=None)

    def remove_rows(self):
        selected = self.tableview.selectedIndexes()
        if selected:
            rows = {i.row() for i in selected}
            self.model.removeRows(row=selected[0].row(), count=len(rows), parent=None)


def main(*args, **kwargs) -> int:
    app = qtw.QApplication(*args, **kwargs)
    mw = MainWindow()
    mw.show()
    return app.exec()


if __name__ == "__main__":
    import sys

    main_rv = main(sys.argv)
    sys.exit(main_rv)
