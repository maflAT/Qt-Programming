from enum import Enum
from typing import Optional, Union, Callable
from PyQt6.QtGui import (
    QAction,
    QBitmap,
    QBrush,
    QColor,
    QFont,
    QKeyEvent,
    QPainter,
    QPen,
    QTransform,
)
from PyQt6.QtCore import (
    QPropertyAnimation,
    QRectF,
    QSize,
    Qt,
    pyqtBoundSignal,
    pyqtSignal,
)
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsBlurEffect,
    QGraphicsObject,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
    QSizePolicy,
    QStyleOptionGraphicsItem,
    QWidget,
)


SIGNAL = Union[pyqtSignal, pyqtBoundSignal]
SLOT = Union[Callable[..., None], pyqtBoundSignal]

SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
BORDER_HEIGHT: int = 100


class Tank(QGraphicsObject):
    BOTTOM: int = 0
    TOP: int = 1
    TANK_BITMAP = b"\x18\x18\xFF\xFF\xFF\xFF\xFF\x66"
    #    ##
    #    ##
    # ########
    # ########
    # ########
    # ########
    # ########
    #  ##  ##

    def __init__(self, color: QColor, y_pos: float, side: int = TOP) -> None:
        super().__init__()
        self.side = side

        # -----------------
        # draw tank object
        # -----------------

        self.bitmap = QBitmap.fromData(QSize(8, 8), self.TANK_BITMAP)
        transform = QTransform()
        transform.scale(4, 4)  # scale to 32 x 32
        if self.side == self.TOP:
            transform.rotate(180)
        self.bitmap = self.bitmap.transformed(transform)
        self.pen = QPen(QColor(color))
        if self.side == self.BOTTOM:
            y_pos -= self.bitmap.height()
        self.setPos(0, y_pos)

        # -----------------
        # create animation
        # -----------------
        # Move left to right across the screen and bounce back on the edges.

        self.animation = QPropertyAnimation(self, b"x")  # applies animation to "self.x"
        self.animation.setStartValue(0)
        self.animation.setEndValue(SCREEN_WIDTH - self.bitmap.width())
        self.animation.setDuration(2000)
        self.animation.finished.connect(self.toggle_direction)

        if self.side == self.TOP:
            self.toggle_direction()
        self.animation.start()

        if self.side == self.BOTTOM:
            bullet_y = y_pos - self.bitmap.height()
        else:
            bullet_y = y_pos + self.bitmap.height()
        self.bullet = Bullet(bullet_y, self.side == self.BOTTOM)

    def shoot(self):
        if not self.bullet.scene():
            self.scene().addItem(self.bullet)
            self.bullet.shoot(self.x())

    # --------------------
    # animation helpers #
    # --------------------

    def toggle_direction(self):
        if self.animation.direction() == QPropertyAnimation.Direction.Forward:
            self.left()
        else:
            self.right()

    def right(self):
        self.animation.setDirection(QPropertyAnimation.Direction.Forward)
        self.animation.start()

    def left(self):
        self.animation.setDirection(QPropertyAnimation.Direction.Backward)
        self.animation.start()

    #############
    # Overrides #
    #############

    def paint(self, painter: QPainter, option, widget) -> None:
        """Overrides QGraphicsItem"""
        painter.setPen(self.pen)
        painter.drawPixmap(0, 0, self.bitmap)

    def boundingRect(self) -> QRectF:
        """Overrides QGraphicsItem"""
        return QRectF(0, 0, self.bitmap.width(), self.bitmap.height())


class Bullet(QGraphicsObject):
    hit: SIGNAL = pyqtSignal()

    def __init__(self, y_pos: float, up: bool = True) -> None:
        super().__init__()
        self.up = up
        self.y_pos = y_pos

        # add some graphics effects:

        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(2)
        blur.setBlurHints(QGraphicsBlurEffect.BlurHint.AnimationHint)
        self.setGraphicsEffect(blur)

        # animation:

        self.animation = QPropertyAnimation(self, b"y")
        self.animation.setStartValue(y_pos)
        end = 0 if up else SCREEN_HEIGHT
        self.animation.setEndValue(end)
        self.animation.setDuration(1000)

        self.yChanged.connect(self.check_collision)

    def shoot(self, x_pos: float):
        self.animation.stop()
        self.setPos(x_pos, self.y_pos)
        self.animation.start()

    def check_collision(self):
        if colliding_items := self.collidingItems():
            self.scene().removeItem(self)
            for item in colliding_items:
                if isinstance(item, Tank):
                    self.hit.emit()

    def boundingRect(self) -> QRectF:
        """Overrices QGraphicsItem
        Represents the bullets draw area."""
        return QRectF(0, 0, 10, 10)

    def paint(self, painter: QPainter, option, widget) -> None:
        """Overrices QGraphicsItem"""
        painter.setBrush(QBrush(QColor("yellow")))
        painter.drawRect(0, 0, 10, 10)


class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setBackgroundBrush(QBrush(QColor("black")))
        self.setSceneRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        wall_brush = QBrush(QColor("grey"), Qt.BrushStyle.Dense5Pattern)
        floor = self.addRect(
            QRectF(0, SCREEN_HEIGHT - BORDER_HEIGHT, SCREEN_WIDTH, BORDER_HEIGHT),
            brush=wall_brush,
        )
        ceiling = self.addRect(
            QRectF(0, 0, SCREEN_WIDTH, BORDER_HEIGHT), brush=wall_brush
        )
        self.top_score = 0
        self.bottom_score = 0
        score_font = QFont("Sans", 32)
        self.top_score_display = self.addText(str(self.top_score), score_font)
        self.top_score_display.setPos(10, 10)
        self.bottom_score_display = self.addText(str(self.bottom_score), score_font)
        self.bottom_score_display.setPos(SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60)

        self.player_top = Tank(QColor("magenta"), ceiling.rect().bottom(), Tank.TOP)
        self.addItem(self.player_top)
        self.player_bottom = Tank(QColor("darkred"), floor.rect().top(), Tank.BOTTOM)
        self.addItem(self.player_bottom)

        self.player_top.bullet.hit.connect(self.top_score_increment)
        self.player_bottom.bullet.hit.connect(self.bottom_score_increment)

    #####################
    # Keyboard Controls #
    #####################

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Overrides QGraphicsScene

        This event is called every time a key is pressed while Scene is focused."""

        keymap: dict[Union[Enum, int], Callable] = {
            Qt.Key.Key_Right: self.player_bottom.right,
            Qt.Key.Key_Left: self.player_bottom.left,
            Qt.Key.Key_Return: self.player_bottom.shoot,
            Qt.Key.Key_A: self.player_top.left,
            Qt.Key.Key_D: self.player_top.right,
            Qt.Key.Key_Space: self.player_top.shoot,
        }
        if callback := keymap.get(event.key()):
            callback()

    def top_score_increment(self):
        self.top_score += 1
        self.top_score_display.setPlainText(str(self.top_score))

    def bottom_score_increment(self):
        self.bottom_score += 1
        self.bottom_score_display.setPlainText(str(self.bottom_score))


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.scene = Scene()
        view = QGraphicsView(self.scene)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(view)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
