from psutil import cpu_percent
from collections import deque
from typing import Union, Callable
from PyQt6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QLinearGradient,
    QPaintEvent,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtCore import QPointF, QTimer, Qt, pyqtBoundSignal, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget


SIGNAL = Union[pyqtSignal, pyqtBoundSignal]
SLOT = Union[Callable[..., None], pyqtBoundSignal]


class GraphWidget(QWidget):
    """A widget to display a running graph of information."""

    crit_color = QColor(255, 0, 0)
    warn_color = QColor(255, 255, 0)
    good_color = QColor(0, 255, 0)

    def __init__(
        self,
        *args,
        data_width: int = 100,
        minimum: int = 0,
        maximum: int = 100,
        warn_val: int = 50,
        crit_val: int = 75,
        scale: int = 5,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.minimum = minimum
        self.maximum = maximum
        self.warn_val = warn_val
        self.scale = scale
        self.crit_val = crit_val

        self.values: deque[float] = deque(
            [self.minimum] * data_width, maxlen=data_width
        )
        self.setFixedWidth(data_width * scale)

    def add_value(self, value: float):
        value = max(value, self.minimum)
        value = min(value, self.maximum)
        self.values.append(value)
        self.update()

    def paintEvent(self, paint_event: QPaintEvent) -> None:
        """Override event of QWidget"""
        # initialize custom QPainter with ourself as target paint device.
        painter = QPainter(self)

        brush = QBrush(QColor(48, 48, 48))
        painter.setBrush(brush)
        painter.drawRect(0, 0, self.width(), self.height())

        pen = QPen()
        pen.setDashPattern([1, 0])
        warn_y = self.val_to_y(self.warn_val)
        pen.setColor(self.warn_color)
        painter.setPen(pen)
        painter.drawLine(0, warn_y, self.width(), warn_y)
        crit_y = self.val_to_y(self.crit_val)
        pen.setColor(self.crit_color)
        painter.setPen(pen)
        painter.drawLine(0, crit_y, self.width(), crit_y)

        # ----------------
        # draw a gradient
        # ----------------

        gradient = QLinearGradient(QPointF(0, self.height()), QPointF(0, 0))
        gradient.setColorAt(0, self.good_color)
        gradient.setColorAt(
            self.warn_val / (self.maximum - self.minimum), self.warn_color
        )
        gradient.setColorAt(
            self.crit_val / (self.maximum - self.minimum), self.crit_color
        )
        brush = QBrush(gradient)
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)

        self.start_value = getattr(self, "start_value", self.minimum)
        last_value = self.start_value
        self.start_value = self.values[0]
        for indx, value in enumerate(self.values):
            x = (indx + 1) * self.scale
            last_x = indx * self.scale
            y = self.val_to_y(value)
            last_y = self.val_to_y(last_value)

            path = QPainterPath()
            path.moveTo(x, self.height())
            path.lineTo(last_x, self.height())
            path.lineTo(last_x, last_y)
            # path.lineTo(x, y)
            # cubic bezier curve:
            c_x = round(self.scale * 0.5) + last_x
            c1 = (c_x, last_y)
            c2 = (c_x, y)
            path.cubicTo(*c1, *c2, x, y)

            painter.drawPath(path)
            last_value = value

    def val_to_y(self, value: float) -> int:
        data_range = self.maximum - self.minimum
        value_fraction = value / data_range
        y_offset = round(value_fraction * self.height())
        return self.height() - y_offset


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.graph = GraphWidget()
        self.setCentralWidget(self.graph)

        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start()

    def update_graph(self):
        cpu_usage = cpu_percent()
        self.graph.add_value(cpu_usage)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
