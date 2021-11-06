from typing import Optional, Union, Callable
from PySide6.QtGui import QAction
from PySide6.QtCore import QUrl, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QTabWidget,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineSettings,
)


SIGNAL = Signal
SLOT = Union[Callable[..., None], Signal]


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, windowTitle="Simple Browser", **kwargs)

        # ------------------
        # Navigation Toolbar
        # ------------------
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

        # ----------------
        # Web Enginge View
        # ----------------
        self.tabs = QTabWidget(tabsClosable=True, movable=True)
        self.tabs.tabCloseRequested.connect(self.tabs.removeTab)
        self.new = QPushButton("New")
        self.tabs.setCornerWidget(self.new)
        self.setCentralWidget(self.tabs)

        # ------------
        # History dock
        # ------------

        history_dock = QDockWidget("History")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, history_dock)
        self.history_list = QListWidget()
        history_dock.setWidget(self.history_list)

        # ---------------
        # connect actions
        # ---------------
        self.back.triggered.connect(self.on_back)
        self.forward.triggered.connect(self.on_forward)
        self.reload.triggered.connect(self.on_reload)
        self.stop.triggered.connect(self.on_stop)
        self.go.triggered.connect(self.on_go)
        self.urlbar.returnPressed.connect(self.on_go)
        self.new.clicked.connect(self.add_tab)
        self.tabs.currentChanged.connect(self.update_history)
        self.history_list.itemDoubleClicked.connect(self.navigate_history)

        # -------------------
        # Global User Profile
        # -------------------
        self.profile = QWebEngineProfile.defaultProfile()
        settings = self.profile.settings()
        settings.setFontFamily(QWebEngineSettings.FontFamily.SansSerifFont, "Impact")
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)

        self.add_tab()

    def add_tab(self, *args):
        webview = QWebEngineView()
        tab_index = self.tabs.addTab(webview, "New Tab")

        # Connect urlChanged Signal to keep address bar, tab title and history in sync
        # with the displayed page. The QWebEngineView object's urlChanged signal is
        # emitted whenever a new URL is loaded into the view.
        webview.urlChanged.connect(
            lambda x: self.tabs.setTabText(tab_index, x.toString())
        )
        webview.urlChanged.connect(lambda x: self.urlbar.setText(x.toString()))
        webview.urlChanged.connect(self.update_history)

        # override createWindow method to support opening pop-ups and new window links
        # in a new tab:
        webview.createWindow = self.add_tab

        # ---------------------
        # assign global profile
        # ---------------------
        page = QWebEnginePage(self.profile)
        webview.setPage(page)

        # set default content for new tab:
        webview.setHtml(
            "<h1>Blank Tab</h1><p>It is a blank tab!</p>", QUrl("about:blank")
        )

        return webview

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

    def update_history(self, *args):
        self.history_list.clear()
        webview: Optional[QWebEngineView] = self.tabs.currentWidget()
        if webview:
            history = webview.history()
            for history_item in reversed(history.items()):
                list_item = QListWidgetItem()
                list_item.setData(Qt.ItemDataRole.DisplayRole, history_item.url())
                self.history_list.addItem(list_item)

    def navigate_history(self, item: QListWidgetItem):
        qurl = item.data(Qt.ItemDataRole.DisplayRole)
        if self.tabs.currentWidget():
            self.tabs.currentWidget().load(qurl)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.showMaximized()
    rv = app.exec()
    sys.exit(rv)
