from typing import Union, Callable
from PySide6.QtGui import QAction
from PySide6.QtCore import QUrl, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTabWidget,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage


SIGNAL = Signal
SLOT = Union[Callable[..., None], Signal]


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, windowTitle="Simple Browser", **kwargs)

        ######################
        # Navigation Toolbar #
        ######################

        navigation = self.addToolBar("Navigation")
        style = self.style()
        self.back = navigation.addAction("Back")
        self.back.setIcon(style.standardIcon(style.StandardPixmap.SP_ArrowBack))
        self.forward = navigation.addAction("Forward")
        self.forward.setIcon(style.standardIcon(style.StandardPixmap.SP_ArrowForward))
        self.reload = navigation.addAction("Reload")
        self.reload.setIcon(style.standardIcon(style.StandardPixmap.SP_BrowserReload))
        self.stop = navigation.addAction("Stop")
        self.stop.setIcon(style.standardIcon(style.StandardPixmap.SP_BrowserStop))
        self.urlbar = QLineEdit()
        navigation.addWidget(self.urlbar)
        self.go = navigation.addAction("Go")
        self.go.setIcon(style.standardIcon(style.StandardPixmap.SP_DialogOkButton))

        ####################
        # Web Enginge View #
        ####################

        self.tabs = QTabWidget(tabsClosable=True, movable=True)
        self.tabs.tabCloseRequested.connect(self.tabs.removeTab)
        self.new = QPushButton("New")
        self.tabs.setCornerWidget(self.new)
        self.setCentralWidget(self.tabs)
        self.add_tab()

    def add_tab(self, *args):
        webview = QWebEngineView()
        tab_index = self.tabs.addTab(webview, "New Tab")

        # Connect urlChanged Signal to keep address bar and tab title in sync with the
        # displayed page. The QWebEngineView object's urlChanged signal is emitted
        # whenever a new URL is loaded into the view.
        webview.urlChanged.connect(
            lambda x: self.tabs.setTabText(tab_index, x.toString())
        )
        webview.urlChanged.connect(lambda x: self.urlbar.setText(x.toString()))

        # set default content for new tab:
        webview.setHtml(
            "<h1>Blank Tab</h1><p>It is a blank tab!</p>", QUrl("about:blank")
        )

        # connect actions
        self.back.triggered.connect(self.on_back)
        self.forward.triggered.connect(self.on_forward)
        self.reload.triggered.connect(self.on_reload)
        self.stop.triggered.connect(self.on_stop)
        self.go.triggered.connect(self.on_go)
        self.urlbar.returnPressed.connect(self.on_go)
        self.new.clicked.connect(self.add_tab)

    def on_back(self):
        self.tabs.currentWidget().back()

    def on_forward(self):
        self.tabs.currentWidget().forward()

    def on_reload(self):
        self.tabs.currentWidget().reload()

    def on_stop(self):
        self.tabs.currentWidget().stop()

    def on_go(self):
        self.tabs.currentWidget().load(QUrl(self.urlbar.text()))


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.showMaximized()
    rv = app.exec()
    sys.exit(rv)
