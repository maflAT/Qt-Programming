from collections import namedtuple
from typing import Any, NamedTuple, Optional, Union, Callable
from PyQt6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QFontInfo,
    QIcon,
    QImage,
    QPainter,
    QPixmap,
)
from PyQt6.QtCore import (
    QDir,
    QFileInfo,
    QRect,
    QSize,
    Qt,
    pyqtBoundSignal,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtWidgets import (
    QApplication,
    QColorDialog,
    QFileDialog,
    QFontDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QWidget,
)


SIGNAL = Union[pyqtSignal, pyqtBoundSignal]
SLOT = Union[Callable[..., None], pyqtBoundSignal]


class DrawSettings(NamedTuple):
    image_source: Optional[str]
    top_text: str
    bottom_text: str
    text_color: QColor
    text_font: QFont
    bg_color: QColor
    top_bg_height: int
    bottom_bg_height: int
    bg_padding: int


class ColorButton(QPushButton):
    changed: SIGNAL = pyqtSignal()

    def __init__(self, default_color, changed: SLOT = None):
        super().__init__()
        self.set_color(QColor(default_color))
        self.clicked.connect(self.on_click)
        # allow connecting changed signal by keyword:
        if changed:
            self.changed.connect(changed)

    def set_color(self, color: QColor):
        self._color = color
        pixmap = QPixmap(32, 32)
        pixmap.fill(self._color)
        self.setIcon(QIcon(pixmap))

    @pyqtSlot()
    def on_click(self):
        color = QColorDialog.getColor(self._color)
        if color:
            self.set_color(color)
            self.changed.emit()


class FontButton(QPushButton):
    changed: SIGNAL = pyqtSignal()

    def __init__(self, default_family: str, default_size: int, changed: SLOT = None):
        super().__init__()
        self.set_font(QFont(default_family, default_size))
        self.clicked.connect(self.on_click)
        if changed:
            self.changed.connect(changed)

    def set_font(self, font: QFont):
        self._font = font
        self.setFont(font)
        self.setText(f"{font.family()} {font.pointSize()}")

    @pyqtSlot()
    def on_click(self):
        font, accepted = QFontDialog.getFont(self._font)
        if accepted:
            self.set_font(font)
            self.changed.emit()


class ImageFileButton(QPushButton):
    changed: SIGNAL = pyqtSignal()

    def __init__(self, changed: SLOT = None):
        super().__init__("Click to select...")
        self._filename = None
        self.clicked.connect(self.on_click)
        if changed:
            self.changed.connect(changed)

    @pyqtSlot()
    def on_click(self):
        filename, _ = QFileDialog.getOpenFileName(
            None,
            "Select an image to use",
            QDir.homePath(),
            "Images (*.png *.xpm *.jpg)",
        )
        if filename:
            self._filename = filename
            self.setText(QFileInfo(filename).fileName())
            self.changed.emit()


class MemeEditForm(QWidget):
    changed: SIGNAL = pyqtSignal(DrawSettings)

    def __init__(self):
        super().__init__()
        layout: QLayout = QFormLayout()
        self.setLayout(layout)

        self.image_source = ImageFileButton(changed=self.on_change)
        layout.addRow("Image file", self.image_source)

        self.top_text = QPlainTextEdit(textChanged=self.on_change)
        layout.addRow("Top Text", self.top_text)
        self.bottom_text = QPlainTextEdit(textChanged=self.on_change)
        layout.addRow("Bottom Text", self.bottom_text)
        self.text_color = ColorButton("white", self.on_change)
        layout.addRow("Text Color", self.text_color)
        self.text_font = FontButton("Impact", 32, self.on_change)
        layout.addRow("Text Font", self.text_font)
        self.text_bg_color = ColorButton("black", changed=self.on_change)
        layout.addRow("Text Background", self.text_bg_color)
        self.top_bg_height = QSpinBox(
            minimum=0, maximum=32, valueChanged=self.on_change, suffix=" line(s)"
        )
        layout.addRow("Top BG Height", self.top_bg_height)
        self.bottom_bg_height = QSpinBox(
            minimum=0, maximum=32, valueChanged=self.on_change, suffix=" line(s)"
        )
        layout.addRow("Bottom BG Height", self.bottom_bg_height)
        self.bg_padding = QSpinBox(
            minimum=0, maximum=100, valueChanged=self.on_change, suffix=" px"
        )
        layout.addRow("BG Padding", self.bg_padding)

    def get_data(self) -> DrawSettings:
        return DrawSettings(
            image_source=self.image_source._filename,
            top_text=self.top_text.toPlainText(),
            bottom_text=self.bottom_text.toPlainText(),
            text_color=self.text_color._color,
            text_font=self.text_font._font,
            bg_color=self.text_bg_color._color,
            top_bg_height=self.top_bg_height.value(),
            bottom_bg_height=self.bottom_bg_height.value(),
            bg_padding=self.bg_padding.value(),
        )

    def on_change(self):
        self.changed.emit(self.get_data())


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, windowTitle="Qt Meme Generator", **kwargs)
        self.max_size = QSize(800, 600)
        self.image = QImage(self.max_size, QImage.Format.Format_ARGB32)
        self.image.fill(QColor("black"))
        mainwidget = QWidget()
        self.setCentralWidget(mainwidget)
        ml = QHBoxLayout()
        mainwidget.setLayout(ml)
        self.image_display = QLabel(pixmap=QPixmap(self.image))
        ml.addWidget(self.image_display)
        self.form = MemeEditForm()
        ml.addWidget(self.form)
        self.form.changed.connect(self.build_image)

        # ---------------
        # create toolbar
        # ---------------

        toolbar = self.addToolBar("File")
        toolbar.addAction("Save Image", self.save_image)

    def build_image(self, data: DrawSettings):
        if not data.image_source:
            self.image.fill(QColor("black"))
        else:
            self.image.load(data.image_source)
            if not (self.max_size - self.image.size()).isValid():
                # isValid returns false if either dimension is negative
                self.image = self.image.scaled(
                    self.max_size, Qt.AspectRatioMode.KeepAspectRatio
                )

        #######################
        # Initialize QPainter #
        #######################

        painter = QPainter(self.image)

        font_px = QFontInfo(data.text_font).pixelSize()
        top_px = (data.top_bg_height * font_px) + data.bg_padding
        top_block_rect = QRect(0, 0, self.image.width(), top_px)
        bottom_px = (
            self.image.height() - data.bg_padding - (data.bottom_bg_height * font_px)
        )
        bottom_block_rect = QRect(0, bottom_px, self.image.width(), self.image.height())

        painter.setBrush(QBrush(data.bg_color))
        painter.drawRect(top_block_rect)
        painter.drawRect(bottom_block_rect)

        painter.setPen(data.text_color)
        painter.setFont(data.text_font)
        flags = Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextWordWrap
        painter.drawText(
            self.image.rect(), flags | Qt.AlignmentFlag.AlignTop, data.top_text
        )
        painter.drawText(
            self.image.rect(), flags | Qt.AlignmentFlag.AlignBottom, data.bottom_text
        )

        self.image_display.setPixmap(QPixmap(self.image))

    def save_image(self):
        save_file, _ = QFileDialog.getSaveFileName(
            None, "Save your image", QDir.homePath(), "PNG Images (*.png)"
        )
        if save_file:
            self.image.save(save_file, "PNG")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
