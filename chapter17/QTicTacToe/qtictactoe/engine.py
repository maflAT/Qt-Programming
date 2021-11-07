from typing import Optional, Union, Callable
from PyQt6.QtCore import QObject, pyqtBoundSignal, pyqtSignal


SIGNAL = Union[pyqtSignal, pyqtBoundSignal]
SLOT = Union[Callable[..., None], pyqtBoundSignal]


class TicTacToeEngine(QObject):
    winning_sets = [
        {0, 1, 2},
        {3, 4, 5},
        {6, 7, 8},
        {0, 3, 6},
        {1, 4, 7},
        {2, 5, 8},
        {0, 4, 8},
        {2, 4, 6},
    ]
    players = ("X", "O")

    game_won: SIGNAL = pyqtSignal(str)
    game_draw: SIGNAL = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.board: list[Optional[str]] = [None] * 9
        self.current_player = self.players[0]

    def next_player(self):
        self.current_player = self.players[not self.players.index(self.current_player)]

    def mark_square(self, square: int) -> bool:
        if any(
            [
                not isinstance(square, int),
                not (0 <= square < len(self.board)),
                self.board[square] is not None,
            ]
        ):
            return False
        self.board[square] = self.current_player
        self.next_player()
        return True

    def check_board(self):
        for player in self.players:
            plays = {idx for idx, value in enumerate(self.board) if value == player}
            for win in self.winning_sets:
                if not win - plays:  # player has winning combo
                    self.game_won.emit(player)
                    return
            if None not in self.board:
                self.game_draw.emit()
