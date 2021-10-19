from pathlib import Path
from PyQt6.QtCore import QDate, QModelIndex, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDataWidgetMapper,
    QDateEdit,
    QFormLayout,
    QHeaderView,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QTableView,
    QWidget,
)
from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlRelation,
    QSqlRelationalDelegate,
    QSqlRelationalTableModel,
    QSqlTableModel,
)


class DateDelegate(QStyledItemDelegate):
    """Custom delegate for editing date values."""

    def createEditor(
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,
        proxyModelIndex: QModelIndex,
    ) -> QWidget:
        return QDateEdit(parent, calendarPopup=True)


class CoffeeForm(QWidget):
    def __init__(
        self, coffees_model: QSqlRelationalTableModel, reviews_model: QSqlTableModel
    ) -> None:
        super().__init__()
        self.coffees_model = coffees_model

        # create form elements:
        self.coffee_brand = QLineEdit()
        self.coffee_name = QLineEdit()
        self.roast = QComboBox()

        self.new_review = QPushButton("New Review", clicked=self.add_review)
        self.delete_review = QPushButton("Delete Review", clicked=self.del_review)

        # ------------------------------
        # configure reviews view / model
        # ------------------------------

        self.reviews = QTableView()
        self.reviews.setModel(reviews_model)
        self.reviews.hideColumn(0)
        self.reviews.hideColumn(1)
        self.reviews.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch
        )
        self.reviews.setItemDelegateForColumn(
            reviews_model.fieldIndex("review_date"), DateDelegate()
        )

        # arrange elements:
        layout = QFormLayout()
        layout.addRow("Brand: ", self.coffee_brand)
        layout.addRow("Name: ", self.coffee_name)
        layout.addRow("Roast: ", self.roast)
        layout.addRow(self.reviews)
        layout.addRow(self.new_review, self.delete_review)
        self.setLayout(layout)

        ##########################################################################
        # Use a DataWidgetMapper to map fields from a model to widgets in a form #
        ##########################################################################

        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.coffees_model)

        # -----------------------------------------------------------------------
        # set a delegate to ensure data is written properly to relational fields:
        # -----------------------------------------------------------------------
        self.mapper.setItemDelegate(QSqlRelationalDelegate(self))

        # ----------------------------------
        # associate widgets to model fields:
        # ----------------------------------
        self.mapper.addMapping(
            self.coffee_brand, self.coffees_model.fieldIndex("coffee_brand")
        )
        self.mapper.addMapping(
            self.coffee_name, self.coffees_model.fieldIndex("coffee_name")
        )
        self.mapper.addMapping(self.roast, self.coffees_model.fieldIndex("description"))

        # ---------------------------------------------------------
        # populate roasts combobox with data from the related table
        # ---------------------------------------------------------

        roasts_model = self.coffees_model.relationModel(
            self.coffees_model.fieldIndex("description")
        )
        self.roast.setModel(roasts_model)
        self.roast.setModelColumn(1)

    def show_coffee(self, coffee_index: QModelIndex):
        """Select record from coffee model by coffee_index."""
        self.mapper.setCurrentIndex(coffee_index.row())

        # ---------------------
        # find matching reviews
        # ---------------------

        # get primary key of current record:
        id_index = coffee_index.siblingAtColumn(0)
        self.coffee_id = int(self.coffees_model.data(id_index))

        # construct SELECT query:
        model: QSqlTableModel = self.reviews.model()
        model.setFilter(f"coffee_id = {self.coffee_id}")  # condition of WHERE clause
        model.setSort(3, Qt.SortOrder.DescendingOrder)  # ORDER BY clause
        model.select()

        self.reviews.resizeRowsToContents()
        self.reviews.resizeColumnsToContents()

    def add_review(self):
        """Create a new record in reviews for selected coffee."""
        model: QSqlTableModel = self.reviews.model()
        new_row = model.record()
        defaults = {
            "coffee_id": self.coffee_id,
            "review_date": QDate.currentDate(),
            "reviewer": "",
            "review": "",
        }
        for field, value in defaults.items():
            index = model.fieldIndex(field)
            new_row.setValue(index, value)

        inserted = model.insertRecord(-1, new_row)
        if not inserted:
            error = model.lastError().text()
            print(f"Insert Failed: {error}")
        model.select()

    def del_review(self):
        """Delete review for selected coffee."""
        for index in self.reviews.selectedIndexes():
            self.reviews.model().removeRow(index.row())
        self.reviews.model().select()


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

        # ------------------------------
        # create review model from table
        # ------------------------------

        self.reviews_model = QSqlTableModel()
        self.reviews_model.setTable("reviews")

        # -----------------------------------------------
        # create model for coffee list from joined tables
        # -----------------------------------------------

        self.coffees_model = QSqlRelationalTableModel()
        self.coffees_model.setTable("coffees")

        # realize relation to roast description withing coffees_model
        # by joining with roasts table:
        self.coffees_model.setRelation(
            self.coffees_model.fieldIndex("roast_id"),
            QSqlRelation("roasts", "id", "description"),
        )

        # --------------------------------------------------------------
        # generate and run a sql select query to refresh the models data
        # --------------------------------------------------------------

        self.coffees_model.select()

        # -------------------------------
        # associate coffee list with data
        # -------------------------------

        self.coffee_list = QTableView()
        self.coffee_list.setModel(self.coffees_model)
        self.stack.addWidget(self.coffee_list)
        self.stack.setCurrentWidget(self.coffee_list)

        # To automatically show a combobox instead of a line edit for editing a foreign
        # relation field, we can set the QSqlRelationalDelegate.
        self.coffee_list.setItemDelegate(QSqlRelationalDelegate())

        # --------------------------------
        # initialize coffee form with data
        # --------------------------------

        self.coffee_form = CoffeeForm(
            coffees_model=self.coffees_model, reviews_model=self.reviews_model
        )
        self.stack.addWidget(self.coffee_form)

        # --------------------
        # customize appearance
        # --------------------

        self.coffee_list.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        ##############
        # Navigation #
        ##############

        toolbar = self.addToolBar("Navigation")
        toolbar.addAction("Delete Coffee(s)", self.delete_coffee)
        toolbar.addAction("Add Coffee(s)", self.add_coffee)
        toolbar.addAction("Back to list", self.show_list)

        # -------------------
        # connect coffee form
        # -------------------

        self.coffee_list.doubleClicked.connect(self.coffee_form.show_coffee)
        self.coffee_list.doubleClicked.connect(
            lambda x: self.stack.setCurrentWidget(self.coffee_form)
        )

    def delete_coffee(self):
        """Delete selected item in coffee list from the database."""
        selected = self.coffee_list.selectedIndexes()
        for index in selected:
            self.coffees_model.removeRow(index.row())

    def add_coffee(self):
        """Add new coffee to the database."""
        self.stack.setCurrentWidget(self.coffee_list)
        self.coffees_model.insertRows(self.coffees_model.rowCount(), 1)

    def show_list(self):
        self.coffee_list.resizeColumnsToContents()
        self.coffee_list.resizeRowsToContents()
        self.stack.setCurrentWidget(self.coffee_list)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow(windowTitle="CoffeeDB")
    mw.show()
    rv = app.exec()
    sys.exit(rv)
