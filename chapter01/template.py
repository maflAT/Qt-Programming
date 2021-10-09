# Template for PyQt / PySide Applications

#####################################
# User Snippets for usage in VSCode #
#####################################

# Custom Widget:
"""
	"pyside6_custom": {
		"prefix": "im qt custom",
		"body": [
			"from PySide6 import QtGui as qtg",
			"from PySide6 import QtCore as qtc",
			"from PySide6 import QtWidgets as qtw ",
			"",
			"",
			"class ${1:CustomWidget}(qtw.${2:QWidget}):",
			"    def __init__(self, *args, **kwargs) -> None:",
			"        super().__init__(*args, **kwargs)",
			"        from ${3:_} import Ui_$4",
			"        Ui_$4().setupUi(self)",
			"        $0",
			"",
			"def main(*args, **kwargs) -> ${5:int}:",
			"    app = qtw.QApplication(*args, **kwargs)",
			"    window = ${1:CustomWidget}()",
			"    window.show()",
			"    return app.exec()",
			"",
			"",
			"if __name__ == \"__main__\":",
			"    import sys",
			"    main_rv = main(sys.argv)",
			"    sys.exit(main_rv)"
		]
	},
"""

# Main Window:
"""
	"pyside6_main": {
		"prefix": "im qt main",
		"body": [
			"from PySide6 import QtGui as qtg",
			"from PySide6 import QtCore as qtc",
			"from PySide6 import QtWidgets as qtw ",
			"",
			"",
			"class ${1:MainWindow}(qtw.${2:QWidget}):",
			"    def __init__(self, *args, **kwargs) -> None:",
			"        super().__init__(*args, **kwargs)",
			"        $0",
			"",
			"def main(*args, **kwargs) -> int:",
			"    app = qtw.QApplication(*args, **kwargs)",
			"    mw = ${1:MainWindow}()",
			"    mw.show()",
			"    return app.exec()",
			"",
			"",
			"if __name__ == \"__main__\":",
			"    import sys",
			"    main_rv = main(sys.argv)",
			"    sys.exit(main_rv)",
			""
		]
	},
"""

from PySide6 import QtGui as qtg
from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw


class MainWindow(qtw.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


def main(*args, **kwargs) -> int:
    app = qtw.QApplication(*args, **kwargs)
    mw = MainWindow()
    mw.show()
    return app.exec()


if __name__ == "__main__":
    import sys

    main_rv = main(sys.argv)
    sys.exit(main_rv)
