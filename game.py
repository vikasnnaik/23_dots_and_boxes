from board import Board
from rules import completed_boxes, move_error

class DotsAndBoxes:
    BOARD_SIZES = {
        "1": ("Small", 2),
        "2": ("Medium", 3),
        "3": ("Large", 4),
    }

    def __init__(self):
        self.board = Board()
        self.current = 0
        self.scores = [0, 0]

    def _select_board(self):
        print("Choose a board size:")
        for choice, (name, boxes) in self.BOARD_SIZES.items():
            print(f"{choice}. {name} ({boxes}x{boxes} boxes)")

        while True:
            choice = input("Board size (1-3): ").strip()
            selected = self.BOARD_SIZES.get(choice)
            if selected is not None:
                _, boxes = selected
                return Board(boxes, boxes)
            print("Invalid board size. Please choose 1, 2, or 3.")

    def play_move(self, orientation, row, col):
        error = move_error(self.board, orientation, row, col)
        if error:
            print(error)
            return False

        before = set(self.board.completed)
        if not self.board.add_line(orientation, row, col):
            return False
        newly_completed = completed_boxes(self.board, before)

        if newly_completed:
            self.scores[self.current] += newly_completed
            print(f"Player {self.current + 1} completed {newly_completed} box(es) and plays again.")
        else:
            self.current = 1 - self.current
        return True

    def run(self):
        print("Dots and Boxes")
        self.board = self._select_board()
        self.current = 0
        self.scores = [0, 0]
        print("Enter moves as H row col or V row col.")
        print("Rows and columns start at 0.")
        print("Example: H 0 1")

        while not self.board.is_complete():
            self.board.display(self.scores, self.current)
            raw = input(f"Player {self.current + 1}, move: ").strip().upper()
            parts = raw.split()

            if len(parts) != 3:
                print("Invalid format.")
                continue

            orientation, row, col = parts
            try:
                row, col = int(row), int(col)
            except ValueError:
                print("Row and column must be valid integers.")
                continue

            self.play_move(orientation, row, col)

        self.board.display(self.scores, self.current)
        print("Game over!")
        if self.scores[0] == self.scores[1]:
            print("The game is a draw.")
        else:
            winner = 1 if self.scores[0] > self.scores[1] else 2
            print(f"Player {winner} wins!")
