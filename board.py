from rules import move_error


class Board:
    def __init__(self, rows=2, cols=2):
        self.rows = rows
        self.cols = cols
        self.horizontal = [[False] * cols for _ in range(rows + 1)]
        self.vertical = [[False] * (cols + 1) for _ in range(rows)]
        self.completed = set()

    def add_line(self, orientation, row, col):
        error = move_error(self, orientation, row, col)
        if error:
            print(error)
            return False

        if orientation == "H":
            self.horizontal[row][col] = True
        else:
            self.vertical[row][col] = True
        self._update_completed()
        return True

    def _update_completed(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if (
                    self.horizontal[r][c]
                    and self.horizontal[r + 1][c]
                    and self.vertical[r][c]
                    and self.vertical[r][c + 1]
                ):
                    self.completed.add((r, c))

    def is_complete(self):
        total = self.rows * (self.cols + 1) + self.cols * (self.rows + 1)
        used = sum(map(sum, self.horizontal)) + sum(map(sum, self.vertical))
        return used == total

    def display(self, scores, current):
        print()
        print(f"Scores: P1={scores[0]}  P2={scores[1]} | Turn: P{current + 1}")

        for r in range(self.rows + 1):
            print(".".join("---" if self.horizontal[r][c] else "   " for c in range(self.cols)))
            if r < self.rows:
                middle = []
                for c in range(self.cols + 1):
                    wall = "|" if self.vertical[r][c] else " "
                    middle.append(wall)
                    if c < self.cols:
                        middle.append(" " + ("X" if (r, c) in self.completed else " ") + " ")
                print("".join(middle))
        print()
