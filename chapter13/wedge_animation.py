from typing import Union, Callable
from PyQt6.QtGui import QAction, QColor, QMatrix4x4, QOpenGLContext, QVector3D
from PyQt6.QtCore import Qt, pyqtBoundSignal, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtOpenGL import (
    QAbstractOpenGLFunctions,
    QOpenGLFunctions_2_1,
    QOpenGLShader,
    QOpenGLShaderProgram,
    QOpenGLVersionFunctionsFactory,
    QOpenGLVersionProfile,
)

SIGNAL = Union[pyqtSignal, pyqtBoundSignal]
SLOT = Union[Callable[..., None], pyqtBoundSignal]


class GlWidget(QOpenGLWidget):
    """A widget to display our OpenGL drawing"""

    def initializeGL(self) -> None:
        """Extends QOpenGLWidget,

        is run once to set up OpenGL drawing."""
        super().initializeGL()

        # -----------------------
        # enable opengl features
        # -----------------------

        gl_context: QOpenGLContext = self.context()
        version = QOpenGLVersionProfile()
        version.setVersion(2, 1)
        # self.gl=gl_context.versionFunctions(version) # Qt5 implementation
        self.gl: QOpenGLFunctions_2_1 = QOpenGLVersionFunctionsFactory.get(
            version, gl_context
        )
        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        self.gl.glDepthFunc(self.gl.GL_LESS)
        self.gl.glEnable(self.gl.GL_CULL_FACE)

        # -------------
        # load shaders
        # -------------

        self.program = QOpenGLShaderProgram()
        self.program.addShaderFromSourceFile(
            QOpenGLShader.ShaderTypeBit.Vertex, "chapter13/vertex_shader.glsl"
        )
        self.program.addShaderFromSourceFile(
            QOpenGLShader.ShaderTypeBit.Fragment, "chapter13/fragment_shader.glsl"
        )
        self.program.link()

        # ------------------------------------------
        # retrieve a handle to our shader variables
        # ------------------------------------------

        self.vertex_location = self.program.attributeLocation("vertex")
        self.matrix_location = self.program.uniformLocation("matrix")
        self.color_location = self.program.attributeLocation("color_attr")

        # ----------------------------
        # configure projection matrix
        # ----------------------------

        self.view_matrix = QMatrix4x4()
        self.view_matrix.perspective(
            45,  # angle
            self.width() / self.height(),  # Aspect ratio
            0.1,  # near clipping plane
            100,  # far clipping plane
        )
        self.view_matrix.translate(0, 0, -5)

    def paintGL(self) -> None:
        """Overrides QOpenGLWidget,
        called on every redraw."""

        # clear canvas:
        self.gl.glClearColor(0.1, 0, 0.2, 1)
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)

        self.program.bind()

        # define geometry and colors:
        front_vertices = [
            QVector3D(0, 1, 0),  # peak
            QVector3D(-1, 0, 0),  # bottom left
            QVector3D(1, 0, 0),  # bottom right
        ]
        face_colors = (
            QColor("red"),
            QColor("orange"),
            QColor("yellow"),
        )
        gl_colors = [self.qcolor_to_glvec(color) for color in face_colors]

        # communicate values to OpenGL:
        self.program.setUniformValue(self.matrix_location, self.view_matrix)
        self.program.enableAttributeArray(self.vertex_location)
        self.program.setAttributeArray(self.vertex_location, front_vertices)
        self.program.enableAttributeArray(self.color_location)
        self.program.setAttributeArray(self.color_location, gl_colors)

        # issue draw command:
        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, 3)

    def qcolor_to_glvec(self, color: QColor):
        return QVector3D(
            color.red() / 255,
            color.green() / 255,
            color.blue() / 255,
        )


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.resize(800, 600)
        main = QWidget()
        self.setCentralWidget(main)
        main.setLayout(QVBoxLayout())
        oglw: GlWidget = GlWidget()
        main.layout().addWidget(oglw)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rv = app.exec()
    sys.exit(rv)
