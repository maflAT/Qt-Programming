import psutil
from collections import deque
from typing import Union, Callable
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout
from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
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


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        tabs = QTabWidget()
        self.setCentralWidget(tabs)
        disk_usage_view = DiskUsageChartView()
        tabs.addTab(disk_usage_view, "Disk Usage")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
