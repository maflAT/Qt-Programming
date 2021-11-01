from enum import Enum
import enum
import psutil
from collections import deque
from typing import Union, Callable
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QKeyEvent,
    QLinearGradient,
    QPainter,
    QPen,
)
from PySide6.QtCore import QEasingCurve, QPoint, QPointF, QTimer, Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout
from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QLegend,
    QSplineSeries,
    QStackedBarSeries,
    QValueAxis,
)


class DiskUsageChartView(QChartView):
    chart_title = "Disk Usage by Partition"

    def __init__(self):
        super().__init__()

        # compose Chart view:
        # * A chart view holds a chart, which only defines the title and not much more.
        # * A chart view can hold one or more different series.
        #   A Series defines the shape of the chart (bar, line, scatter, ...)
        # * A Series can hold one or more sets.
        # * The set contains the actual data.
        self.setChart(chart := QChart(title=self.chart_title))
        chart.addSeries(series := QBarSeries())
        series.setLabelsVisible(True)
        series.append(bar_set := QBarSet("Percent Used"))

        # collect data for the chart:
        partitions = []
        for part in psutil.disk_partitions():
            if "rw" in part.opts.split(","):
                partitions.append(part.device)
                usage = psutil.disk_usage(part.mountpoint)
                bar_set.append(usage.percent)

        # Create axes:
        x_axis = QBarCategoryAxis()
        x_axis.append(partitions)
        chart.setAxisX(x_axis)
        series.attachAxis(x_axis)

        y_axis = QValueAxis()
        y_axis.setRange(0, 100)
        chart.setAxisY(y_axis)
        series.attachAxis(y_axis)


class CPUUsageView(QChartView):
    num_data_points = 500
    chart_title = "CPU Utilization"

    def __init__(self):
        super().__init__()
        self.setChart(chart := QChart(title=self.chart_title))
        self.series = QSplineSeries(name="Percentage")
        chart.addSeries(self.series)

        self.data = deque([0.0] * self.num_data_points, self.num_data_points)
        self.series.append([QPointF(x, y) for x, y in enumerate(self.data)])

        x_axis = QValueAxis()
        x_axis.setRange(0, self.num_data_points)
        x_axis.setLabelsVisible(False)
        y_axis = QValueAxis()
        y_axis.setRange(0, 100)
        chart.setAxisX(x_axis, self.series)
        chart.setAxisY(y_axis, self.series)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.timer = QTimer(interval=200, timeout=self.refresh_stats)
        self.timer.start()

    def refresh_stats(self):
        self.data.append(psutil.cpu_percent())
        new_data = [QPointF(x, y) for x, y in enumerate(self.data)]
        self.series.replace(new_data)

    ############################
    # Override Keypress Events #
    ############################

    # This allows interactive panning and zooming.

    def keyPressEvent(self, event: QKeyEvent) -> None:
        keymap: dict[int, Callable[..., None]] = {
            Qt.Key_Up: lambda: self.chart().scroll(0, -10),
            Qt.Key_Down: lambda: self.chart().scroll(0, 10),
            Qt.Key_Right: lambda: self.chart().scroll(-10, 0),
            Qt.Key_Left: lambda: self.chart().scroll(10, 0),
            Qt.Key_Greater: self.chart().zoomIn,
            Qt.Key_Less: self.chart().zoomOut,
        }
        if callback := keymap.get(event.key()):
            callback()


class MemoryChartView(QChartView):
    chart_title = "Memory Usage"
    num_data_points = 50

    def __init__(self):
        super().__init__()
        self.setChart(chart := QChart(title=self.chart_title))
        chart.addSeries(series := QStackedBarSeries())
        self.phys_set = QBarSet("Physical")
        self.swap_set = QBarSet("Swap")
        series.append(self.phys_set)
        series.append(self.swap_set)

        self.data = deque([(0, 0)] * self.num_data_points, maxlen=self.num_data_points)
        for phys, swap in self.data:
            self.phys_set.append(phys)
            self.swap_set.append(swap)

        x_axis = QValueAxis()
        x_axis.setRange(0, self.num_data_points)
        x_axis.setLabelsVisible(False)
        y_axis = QValueAxis()
        y_axis.setRange(0, 100)
        chart.setAxisX(x_axis, series)
        chart.setAxisY(y_axis, series)

        self.timer = QTimer(interval=1000, timeout=self.refresh_stats)
        self.timer.start()

        # --------------------------
        # Add Styling and Animations
        # --------------------------

        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        chart.setAnimationEasingCurve(QEasingCurve.Type.OutBounce)
        chart.setAnimationDuration(1000)
        chart.setDropShadowEnabled(True)

        chart.setTheme(QChart.ChartTheme.ChartThemeBlueCerulean)

        gradient = QLinearGradient(
            chart.plotArea().topLeft(), chart.plotArea().bottomRight()
        )
        gradient.setColorAt(0, QColor("#333"))
        gradient.setColorAt(1, QColor("#660"))
        chart.setBackgroundBrush(gradient)
        chart.setBackgroundPen(QPen(QColor("black"), 5))

        chart.setTitleBrush(QBrush(Qt.GlobalColor.white))
        chart.setTitleFont(QFont("Impact", 32, QFont.Weight.Bold))

        # ----------------
        # Styling the axes
        # ----------------

        axis_font = QFont("Mono", 16)
        axis_brush = QBrush(QColor("#EEF"))
        y_axis.setLabelsFont(axis_font)
        y_axis.setLabelsBrush(axis_brush)

        grid_pen = QPen(QColor("silver"))
        grid_pen.setDashPattern([1, 1, 1, 0])
        x_axis.setGridLinePen(grid_pen)
        y_axis.setGridLinePen(grid_pen)

        y_axis.setTickCount(11)
        y_axis.setShadesVisible(True)
        y_axis.setShadesColor(QColor("#884"))

        # ------------------
        # styling the legend
        # ------------------

        legend = chart.legend()
        legend.setBackgroundVisible(True)
        legend.setBrush(QBrush(QColor("white")))

        legend.setFont(QFont("Times", 16))
        legend.setLabelColor(QColor(Qt.GlobalColor.darkBlue))

        legend.setMarkerShape(QLegend.MarkerShape.MarkerShapeFromSeries)

    def refresh_stats(self):
        phys = psutil.virtual_memory()
        swap = psutil.swap_memory()
        total_mem = phys.total + swap.total
        phys_pct = (phys.used / total_mem) * 100
        swap_pct = (swap.used / total_mem) * 100

        self.data.append((phys_pct, swap_pct))
        for x, (phys, swap) in enumerate(self.data):
            self.phys_set.replace(x, phys)
            self.swap_set.replace(x, swap)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        disk_usage_view = DiskUsageChartView()
        tabs.addTab(disk_usage_view, "Disk Usage")

        cpu_view = CPUUsageView()
        tabs.addTab(cpu_view, "CPU Usage")

        cpu_time_view = MemoryChartView()
        tabs.addTab(cpu_time_view, "Memory Usage")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
