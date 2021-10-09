from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw


app = qtw.QApplication([])

window = qtw.QWidget()
window.setWindowTitle("Hello")
print(window.windowTitle())
window.show()

app.exec()
