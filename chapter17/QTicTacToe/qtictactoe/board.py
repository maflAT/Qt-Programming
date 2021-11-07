import os, sys
from typing import Union, Callable
from PyQt6.QtGui import QBrush, QPixmap
from PyQt6.QtCore import QRectF, Qt, pyqtBoundSignal, pyqtSignal
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsSceneMouseEvent


SIGNAL = Union[pyqtSignal, pyqtBoundSignal]
SLOT = Union[Callable[..., None], pyqtBoundSignal]

if getattr(sys, "frozen", False):
    ressource_path = sys._MEIPASS
else:
    ressource_path = os.path.dirname(__file__)


class TTTBoard(QGraphicsScene):
    """View class representing the TicTacToe board."""

    square_rects = (
        QRectF(5, 5, 190, 190),
        QRectF(205, 5, 190, 190),
        QRectF(405, 5, 190, 190),
        QRectF(5, 205, 190, 190),
        QRectF(205, 205, 190, 190),
        QRectF(405, 205, 190, 190),
        QRectF(5, 405, 190, 190),
        QRectF(205, 405, 190, 190),
        QRectF(405, 405, 190, 190),
    )

    square_clicked: SIGNAL = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 600, 600)
        self.setBackgroundBrush(QBrush(Qt.GlobalColor.cyan))
        for square in self.square_rects:
            self.addRect(square, brush=QBrush(Qt.GlobalColor.white))
        self.mark_pngs = {
            "X": QPixmap(os.path.join(ressource_path, "images", "X.png")),
            "O": QPixmap(os.path.join(ressource_path, "images", "O.png")),
        }
        self.marks: list[QGraphicsItem] = []

    def set_board(self, marks: list):
        for i, square in enumerate(marks):
            if square in self.mark_pngs:
                mark = self.addPixmap(self.mark_pngs[square])
                mark.setPos(self.square_rects[i].topLeft())
                self.marks.append(mark)

    def clear_board(self):
        for mark in self.marks:
            self.removeItem(mark)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Overrides QGraphicsScene."""
        position = event.buttonDownScenePos(Qt.MouseButton.LeftButton)
        for square, qrect in enumerate(self.square_rects):
            if qrect.contains(position):
                self.square_clicked.emit(square)
                break
