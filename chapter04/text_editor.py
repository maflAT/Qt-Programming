from typing import Optional
from PyQt6 import QtGui as qtg, QtCore as qtc, QtWidgets as qtw


class SettingsDialog(qtw.QDialog):
    """Custom settins dialog"""

    def __init__(
        self,
        settings: qtc.QSettings,
        parent: Optional[qtw.QWidget] = None,
        flags: qtc.Qt.WindowType = qtc.Qt.WindowType.Dialog,
    ) -> None:
        super().__init__(parent=parent, flags=flags)
        self.settings = settings
        self.show_warnings_cb = qtw.QCheckBox(
            checked=settings.value("show_warnings", True, bool)
        )
        self.accept_btn = qtw.QPushButton("OK", clicked=self.accept)
        self.cancel_btn = qtw.QPushButton("Cancel", clicked=self.reject)
        layout = qtw.QFormLayout()
        layout.addRow(qtw.QLabel("<h1>Application Settings</h1>"))
        layout.addRow("Show Warnings", self.show_warnings_cb)
        layout.addRow(self.accept_btn, self.cancel_btn)
        self.setLayout(layout)

    def accept(self) -> None:
        self.settings.setValue("show_warnings", self.show_warnings_cb.isChecked())
        super().accept()


class MainWindow(qtw.QMainWindow):
    """Text editor main window"""

    settings = qtc.QSettings("Alan D Moore", "text editor")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            windowTitle="Simple Text Edit",
            minimumWidth=400,
            minimumHeight=250,
            # font=qtg.QFont("Impact", 12),
            # windowOpacity=0.5,
            **kwargs,
        )

        self.textedit = qtw.QTextEdit()
        self.setCentralWidget(self.textedit)

        ####################
        # Build Status Bar #
        ####################

        self.statusBar().showMessage("Welcome to text_editor.py")
        charcount_label = qtw.QLabel("chars: 0")
        self.statusBar().addPermanentWidget(charcount_label)
        self.textedit.textChanged.connect(
            lambda: charcount_label.setText(
                "chars: " + str(len(self.textedit.toPlainText()))
            )
        )

        ##################
        # Build Menu Bar #
        ##################

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(self.openFile)
        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(self.saveFile)
        file_menu.addAction("Show settings", self.show_settings)
        quit_action = file_menu.addAction("Quit", self.close)
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Undo", self.textedit.undo)

        # explicitly create QAction:
        redo_action = qtg.QAction("Redo", self)
        # explicitly created actions `triggered` signal must be connected manually.
        redo_action.triggered.connect(self.textedit.redo)
        edit_menu.addAction(redo_action)
        edit_menu.addAction("Change Font", self.set_font)
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About", self.showAboutDialog)

        ################
        # Add Toolbars #
        ################

        toolbar = self.addToolBar("File")
        # toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setAllowedAreas(
            qtc.Qt.ToolBarArea.TopToolBarArea | qtc.Qt.ToolBarArea.BottomToolBarArea
        )

        # Actions and Icons:
        toolbar.addAction(open_action)
        open_icon = self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_DirOpenIcon)
        open_action.setIcon(open_icon)
        save_icon = self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_DriveHDIcon)
        toolbar.addAction(
            save_icon, "Save", lambda: self.statusBar().showMessage("File Saved!")
        )
        help_action = qtg.QAction(
            self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_DialogHelpButton),
            "Help",
            self,
            triggered=lambda: self.statusBar().showMessage("Sorry, no help yet!"),
        )
        toolbar.addAction(help_action)

        toolbar2 = qtw.QToolBar("Edit")
        toolbar2.addAction("Copy", self.textedit.copy)
        toolbar2.addAction("Cut", self.textedit.cut)
        toolbar2.addAction("Paste", self.textedit.paste)
        self.addToolBar(qtc.Qt.ToolBarArea.RightToolBarArea, toolbar2)

        ####################
        # Add Dock Widgets #
        ####################

        dock = qtw.QDockWidget("Replace")
        self.addDockWidget(qtc.Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        dock.setFeatures(
            qtw.QDockWidget.DockWidgetFeature.DockWidgetMovable
            | qtw.QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        # Setup Widget:
        self.search_text_inp = qtw.QLineEdit(placeholderText="search")
        self.replace_text_inp = qtw.QLineEdit(placeholderText="replace")
        search_and_replace_btn = qtw.QPushButton(
            "Search and replace", clicked=self.search_and_replace
        )
        s_r_layout = qtw.QVBoxLayout()
        s_r_layout.addWidget(self.search_text_inp)
        s_r_layout.addWidget(self.replace_text_inp)
        s_r_layout.addWidget(search_and_replace_btn)
        s_r_layout.addStretch()
        replace_widget = qtw.QWidget()
        replace_widget.setLayout(s_r_layout)
        dock.setWidget(replace_widget)

        #################
        # Message Boxes #
        #################

        # response = qtw.QMessageBox.question(
        #     self,
        #     "My Text Editor",
        #     "This is beta software, do you want to continue?",
        #     qtw.QMessageBox.StandardButton.Yes | qtw.QMessageBox.StandardButton.Abort,
        # )

        splash_screen = qtw.QMessageBox(
            windowTitle="My Text Editor",
            text="BETA SOFTWARE WARNING!",
            informativeText="This is very, very beta, "
            "are you really sure you want to use it?",
            detailedText="This editor was written for pedagogical purposes, "
            "and probably is not fit for real work.",
            modal=True,
        )
        splash_screen.addButton(qtw.QMessageBox.StandardButton.Yes)
        splash_screen.addButton(qtw.QMessageBox.StandardButton.Abort)

        if self.settings.value("show_warnings", False, type=bool):
            response = splash_screen.exec()
            if response == qtw.QMessageBox.StandardButton.Abort:
                self.close()
                sys.exit()

    def search_and_replace(self):
        s_text = self.search_text_inp.text()
        r_text = self.replace_text_inp.text()
        if s_text:
            self.textedit.setText(self.textedit.toPlainText().replace(s_text, r_text))

    def showAboutDialog(self):
        qtw.QMessageBox.about(
            self,
            "About text_editor.py",
            "This is a text editor written in PyQt.",
        )

    def openFile(self):
        filename, _ = qtw.QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a text file to open...",
            # directory=qtc.QDir.homePath(),
            filter="Text Files (*.txt) ;;Python Files (*.py) ;;All Files (*)",
            initialFilter="Python Files (*.py)",
            options=qtw.QFileDialog.Option.DontResolveSymlinks
            # | qtw.QFileDialog.Option.DontUseNativeDialog,
        )
        if filename:
            try:
                with open(filename, "r") as fh:
                    self.textedit.setText(fh.read())
            except Exception as e:
                qtw.QMessageBox.critical(f"could not load file: {e}")

    def saveFile(self):
        filename, _ = qtw.QFileDialog.getSaveFileName(
            self,
            "Select the file to save to...",
            qtc.QDir.homePath(),
            "Text Files (*.txt) ;;Python Files (*.py) ;; All Files (*)",
        )
        if filename:
            try:
                with open(filename, "w") as fh:
                    fh.write(self.textedit.toPlainText())
            except Exception as e:
                qtw.QMessageBox.critical(f"Could not save file: {e}")

    def set_font(self):
        current = self.textedit.currentFont()
        font, accepted = qtw.QFontDialog.getFont(
            current,
            parent=self,
            options=qtw.QFontDialog.FontDialogOption.MonospacedFonts,
        )
        if accepted:
            self.textedit.setCurrentFont(font)

    def show_settings(self):
        settings_dialog = SettingsDialog(self.settings, self)
        settings_dialog.exec()


def main(*args, **kwargs) -> int:
    app = qtw.QApplication(*args, **kwargs)
    mw = MainWindow()
    mw.show()
    return app.exec()


if __name__ == "__main__":
    import sys

    main_rv = main(sys.argv)
    sys.exit(main_rv)
