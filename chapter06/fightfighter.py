from pathlib import Path
from typing import Optional, Union
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QIcon,
    QLinearGradient,
    QPainter,
    QPalette,
    QPen,
    QPixmap,
)
from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QRect,
    QSequentialAnimationGroup,
    QSize,
    Qt,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProxyStyle,
    QPushButton,
    QStyle,
    QStyleOption,
    QWidget,
)
import resources


class StyleOverrides(QProxyStyle):
    """Overrides style methods globally"""

    def drawItemText(
        self,
        painter: QPainter,
        rect: QRect,
        flags: int,
        pal: Union[QPalette, Qt.GlobalColor, QColor],
        enabled: bool,
        text: str,
        textRole: QPalette.ColorRole = None,
    ) -> None:
        """Force uppercase in all text"""
        text = text.upper()
        return super().drawItemText(
            painter, rect, flags, pal, enabled, text, textRole=textRole
        )

    def drawPrimitive(
        self,
        element: QStyle.PrimitiveElement,
        option: QStyleOption,
        painter: QPainter,
        widget: Optional[QWidget] = None,
    ) -> None:
        """Outline QEdits in green"""

        if element != QStyle.PE_FrameLineEdit:
            return super().drawPrimitive(element, option, painter, widget=widget)

        self.green_pen = QPen(QColor("green"), 4)
        painter.setPen(self.green_pen)
        painter.drawRoundedRect(widget.rect(), 10, 10)


class ColorButton(QPushButton):
    """Button that allows animation of its color via Qt property"""

    def _color(self):
        return self.palette().color(QPalette.ButtonText)

    def _setColor(self, qcolor):
        palette = self.palette()
        palette.setColor(QPalette.ButtonText, qcolor)
        self.setPalette(palette)

    # PySide6 implementation using constructor:
    color = Property(QColor, _color, _setColor)

    # PySide6 implementation using decorators:
    @Property(QColor)
    def bgColor(self):
        return self.palette().color(QPalette.Button)

    @bgColor.setter
    def bgColor(self, qcolor):
        palette = self.palette()
        palette.setColor(QPalette.Button, qcolor)
        self.setPalette(palette)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__(parent=None, windowTitle="Fight Fighter Game Lobby")

        #########################
        # Setup central widget: #
        #########################

        heading = QLabel("Fight Fighter!", alignment=Qt.AlignHCenter)
        inputs: dict[str, QWidget] = {
            "Server": QLineEdit(),
            "Name": QLineEdit(),
            "Password": QLineEdit(echoMode=QLineEdit.EchoMode.Password),
            "Team": QComboBox(),
            "Ready": QCheckBox("Check when ready"),
        }
        teams = ("Crimson Sharks", "Shadow Hawks", "Night Terrors", "Blue Crew")
        inputs["Team"].addItems(teams)
        self.submit = ColorButton(
            "Connect",
            clicked=lambda: QMessageBox.information(
                self, "Connecting", "Prepare for Battle!"
            ),
        )
        self.cancel = ColorButton(text="Cancel", clicked=self.close)
        layout = QFormLayout()
        layout.addRow(heading)
        for label, widget in inputs.items():
            layout.addRow(label, widget)
        layout.addRow(self.submit, self.cancel)
        cx_form = QWidget()
        cx_form.setLayout(layout)
        self.setCentralWidget(cx_form)

        # ==========
        # Set fonts:
        # ==========

        heading_font = QFont(["Impact"], 32, QFont.Weight.Black)
        heading_font.setStretch(QFont.Stretch.Expanded)
        heading.setFont(heading_font)

        label_font = QFont()
        label_font.setFamily("Impact")
        label_font.setPointSize(14)
        label_font.setWeight(QFont.Weight.ExtraLight)
        label_font.setStyle(QFont.Style.StyleItalic)
        for inp in inputs.values():
            layout.labelForField(inp).setFont(label_font)

        # ---------------------
        # handle font fallback:
        # ---------------------

        button_font = QFont("noexists", 14)  # set font
        # print(QFontInfo(button_font).family())            # actual used font
        button_font.setStyleHint(QFont.StyleHint.Fantasy)  # fallback settings
        # print(QFontInfo(button_font).family())  # fallback font
        button_font.setStyleStrategy(
            QFont.StyleStrategy(
                QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.PreferQuality
            )
        )
        self.submit.setFont(button_font)
        self.cancel.setFont(button_font)

        # ------------------
        # Font from rcc file
        # ------------------

        custom_font_id = QFontDatabase.addApplicationFont(":/fonts/BRLNSR.TTF")
        custom_font_family = QFontDatabase.applicationFontFamilies(custom_font_id)[0]
        custom_font = QFont([custom_font_family], 14)
        inputs["Team"].setFont(custom_font)

        ##############
        # Add Images #
        ##############

        logo = QPixmap(str(Path(__file__).parent / "logo.png"))
        # scale image:
        if logo.width() > 400:
            logo = logo.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
        heading.setPixmap(logo)

        # -------------------------
        # create pixmaps on the fly
        # -------------------------

        go_pixmap = QPixmap(QSize(32, 32))
        go_pixmap.fill(QColor("green"))
        stop_pixmap = QPixmap(QSize(32, 32))
        stop_pixmap.fill(QColor("red"))

        # ------
        # QIcons
        # ------

        connect_icon = QIcon()
        connect_icon.addPixmap(go_pixmap, mode=QIcon.Mode.Active)
        connect_icon.addPixmap(stop_pixmap, mode=QIcon.Mode.Disabled)
        self.submit.setIcon(connect_icon)
        self.submit.setDisabled(True)
        inputs["Server"].textChanged.connect(lambda x: self.submit.setDisabled(x == ""))

        # ---------------------
        # Pixmaps from rcc file
        # ---------------------
        # Support for Qt’s resource system has been removed in PyQt6 (i.e. there is no pyrcc6).

        inputs["Team"].setItemIcon(0, QIcon(":/teams/crimson_sharks.png"))
        inputs["Team"].setItemIcon(1, QIcon(":/teams/shadow_hawks.png"))
        inputs["Team"].setItemIcon(2, QIcon(":/teams/night_terrors.png"))
        inputs["Team"].setItemIcon(3, QIcon(":/teams/blue_crew.png"))

        #######################
        # Palettes and colors #
        #######################

        # get palette from running application instance:
        palette: QPalette = QApplication.instance().palette()

        palette.setColor(QPalette.ColorRole.Button, QColor("#333"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#3F3"))
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor("#888")
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#F88")
        )

        self.submit.setPalette(palette)
        self.cancel.setPalette(palette)

        # -------
        # Brushes
        # -------

        dotted_brush = QBrush(QColor("white"), Qt.BrushStyle.Dense4Pattern)

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("navy"))
        gradient.setColorAt(0.5, QColor("darkgrey"))
        gradient.setColorAt(1, QColor("darkred"))
        gradient_brush = QBrush(gradient)

        window_palette: QPalette = QApplication.instance().palette()
        window_palette.setBrush(QPalette.ColorRole.Window, gradient_brush)
        window_palette.setBrush(
            QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, dotted_brush
        )
        self.setPalette(window_palette)

        ###################
        # Qt Style Sheets #
        ###################

        # applied style is automatically inherited by all subclasses
        stylesheet = """
            QMainWindow {
                background-color: black;
            }
            QWidget {
                background-color: transparent;
                color: #3F3;
            }
            QLineEdit, QComboBox, QCheckBox {
                font-size: 16pt;
            }
        """
        # override settings for subclasses of QWidget:
        stylesheet += """
            QPushButton {
                background-color: #333;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid silver;
                background-color: darkred;
            }
            QCheckBox::indicator:checked {
                border: 1px solid silver;
                background-color: #3F3;
            }
        """
        # change style elements without inheriting to subclasses
        bg_sprite = str(Path(__file__).relative_to(Path.cwd()).parent) + "/tile.png"
        stylesheet += """
        .QWidget {
            background: url(%s)
        }
        """ % (
            bg_sprite
        )

        # change style of individual objects instead of the whole class:
        self.submit.setObjectName("SubmitButton")
        stylesheet += """
        #SubmitButton:disabled {
            background-color: #888;
            color: darkred;
        }
        """
        for inp in ("Server", "Name", "Password"):
            inp_widget = inputs[inp]
            inp_widget.setStyleSheet("background-color: black")

        # self.setStyleSheet(stylesheet)

        ##############
        # Animations #
        ##############

        # -------------------
        # property animations
        # -------------------

        self.heading_animation = QPropertyAnimation(heading, b"maximumSize")
        self.heading_animation.setStartValue(QSize(10, logo.height()))
        self.heading_animation.setEndValue(QSize(400, logo.height()))
        self.heading_animation.setDuration(2000)
        self.heading_animation.start()

        # ----------------
        # animating colors
        # ----------------

        self.text_color_animation = QPropertyAnimation(self.submit, b"color")
        self.text_color_animation.setStartValue(QColor("#FFF"))
        self.text_color_animation.setKeyValueAt(0.5, QColor("#888"))
        self.text_color_animation.setEndValue(QColor("#FFF"))
        self.text_color_animation.setLoopCount(-1)
        self.text_color_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.text_color_animation.setDuration(2000)

        self.bg_color_animation = QPropertyAnimation(self.cancel, b"bgColor")
        self.bg_color_animation.setStartValue(QColor("darkgrey"))
        self.bg_color_animation.setKeyValueAt(0.5, QColor("darkred"))
        self.bg_color_animation.setEndValue(QColor("darkgrey"))
        self.bg_color_animation.setLoopCount(-1)
        self.bg_color_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.bg_color_animation.setDuration(2000)

        # ----------------
        # animation groups
        # ----------------

        self.button_animations = QParallelAnimationGroup()
        self.button_animations.addAnimation(self.text_color_animation)
        self.button_animations.addAnimation(self.bg_color_animation)

        self.all_animations = QSequentialAnimationGroup()
        self.all_animations.addAnimation(self.heading_animation)
        self.all_animations.addAnimation(self.button_animations)
        self.all_animations.start()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    ######################
    # Customizing Styles #
    ######################

    proxy_style = StyleOverrides()
    app.setStyle(proxy_style)

    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
