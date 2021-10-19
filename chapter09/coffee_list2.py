from pathlib import Path
from typing import Any
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHeaderView,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)
from PyQt6.QtSql import QSqlDatabase


class CoffeeForm(QWidget):
    def __init__(self, roasts: list[str]) -> None:
        super().__init__()

        # create form elements:
        self.coffee_brand = QLineEdit()
        self.coffee_name = QLineEdit()
        self.roast = QComboBox()
        self.roast.addItems(roasts)
        self.reviews = QTableWidget(columnCount=3)
        self.reviews.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )

        # arrange elements:
        layout = QFormLayout()
        layout.addRow("Brand: ", self.coffee_brand)
        layout.addRow("Name: ", self.coffee_name)
        layout.addRow("Roast: ", self.roast)
        layout.addRow("Reviews: ", self.reviews)
        self.setLayout(layout)

    def show_coffee(self, coffee_data: dict[str, Any], reviews: list[tuple[str]]):
        self.coffee_brand.setText(coffee_data.get("coffee_brand"))
        self.coffee_name.setText(coffee_data.get("coffee_name"))
        self.roast.setCurrentIndex(coffee_data.get("roast_id"))
        self.reviews.clear()
        self.reviews.setHorizontalHeaderLabels(["Reviewer", "Date", "Review"])
        self.reviews.setRowCount(len(reviews))
        for i, review in enumerate(reviews):
            for j, value in enumerate(review):
                self.reviews.setItem(i, j, QTableWidgetItem(value))


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # create main widget:
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        ######################
        # configure database #
        ######################

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(str(Path(__file__).parent.joinpath("coffee.db")))

        # establish and check db connection:
        if not self.db.open():
            error = self.db.lastError().text()
            QMessageBox.critical(
                self, "DB Connection Error", "Could not open database file:", f"{error}"
            )
            sys.exit(1)

        # check catabase structure:
        required_tables = {"roasts", "coffees", "reviews"}
        tables = self.db.tables()
        missing_tables = required_tables - set(tables)
        if missing_tables:
            QMessageBox.critical(
                self,
                "DB Integrity Error",
                f"Missing tables, please repair DB: {missing_tables}",
            )
            sys.exit(1)

        # -----------------------------
        # retrieve data for coffee form
        # -----------------------------

        # --------------------------------
        # initialize coffee form with data
        # --------------------------------

        self.coffee_form = CoffeeForm(...)
        self.stack.addWidget(self.coffee_form)

        # -----------------------------
        # retrieve data for coffee list
        # -----------------------------

        # --------------------------------
        # initialize coffee list with data
        # --------------------------------

        self.coffee_list = QTableView()
        self.coffee_list.setModel(...)
        self.stack.addWidget(self.coffee_list)

        # --------------------
        # customize appearance
        # --------------------

        self.coffee_list.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        self.coffee_list.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )

        ##############
        # Navigation #
        ##############

        navigation = self.addToolBar("Navigation")
        navigation.addAction(
            "Back to list", lambda: self.stack.setCurrentWidget(self.coffee_list)
        )

        self.coffee_list.doubleClicked.connect(
            lambda x: self.show_coffee(self.get_id_for_row(x))
        )

        self.stack.setCurrentWidget(self.coffee_list)

    def show_coffee(self, coffee_id: int):
        """Retrieve data for coffee_id from the db and pass it to coffee_form."""

        # ------------------------
        # query db for coffee data
        # ------------------------

        # -----------------------------
        # query db for matching reviews
        # -----------------------------

        # --------------------------------------------
        # pass data to our form and bring it into view
        # --------------------------------------------

        self.coffee_form.show_coffee(coffee_data=..., reviews=...)
        self.stack.setCurrentWidget(self.coffee_form)

    def get_id_for_row(self, index: ...) -> int:
        ...


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow(windowTitle="CoffeeDB")
    mw.show()
    rv = app.exec()
    sys.exit(rv)
