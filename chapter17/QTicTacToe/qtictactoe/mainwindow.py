from typing import Union, Callable
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal
from PyQt6.QtWidgets import (
    QGraphicsView,
    QMainWindow,
    QMessageBox,
)
from .engine import TicTacToeEngine
from .board import TTTBoard

SIGNAL = Union[pyqtSignal, pyqtBoundSignal]
SLOT = Union[Callable[..., None], pyqtBoundSignal]


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, windowTitle="TicTacToe", **kwargs)
        self.board = TTTBoard()
        self.board_view = QGraphicsView()
        self.board_view.setScene(self.board)
        self.setCentralWidget(self.board_view)

        self.start_game()
        self.board.square_clicked.connect(self.try_mark)

    def start_game(self):
        self.board.clear_board()
        self.game = TicTacToeEngine()
        self.game.game_won.connect(self.game_won)
        self.game.game_draw.connect(self.game_draw)

    def try_mark(self, square):
        if self.game.mark_square(square):
            self.board.set_board(self.game.board)
            self.game.check_board()

    def game_won(self, player):
        """Display the winner and start a new game"""
        QMessageBox.information(None, "Game Won", f"Player {player} won!")
        self.start_game()

    def game_draw(self):
        QMessageBox.information(None, "Game Over", "Game Over. Nobody won...")
        self.start_game()
