# Dots and Boxes - Lab 4

## Run the game

From the project folder, run:

```text
python main.py
```

Choose a board size when prompted:

1. Small: 2x2 boxes
2. Medium: 3x3 boxes
3. Large: 4x4 boxes

Enter each move as `H row col` for a horizontal line or `V row col` for a vertical line. Rows and columns start at zero. For a board with `N` boxes per side, horizontal rows are `0` through `N` and columns are `0` through `N-1`; vertical rows are `0` through `N-1` and columns are `0` through `N`.

Two players take turns. A player who completes a box earns one point for each newly completed box and plays again. Otherwise, the turn passes to the other player.

## Project changes

### Coordinate conversion bug

The original input check used `str.isdigit()` before converting coordinates with `int()`. Some Unicode characters, including superscript two (`²`), return true from `isdigit()` but cannot be parsed by `int()`, which caused a `ValueError` and stopped the game. The game now attempts the integer conversion inside a `try`/`except ValueError` block and prompts again when conversion fails. The board is not changed until the move has passed validation.

### Board sizes

Players can select 2x2, 3x3, or 4x4 boxes before play. The game creates a square `Board` with the selected dimensions. Horizontal and vertical line arrays, box detection, and the end-of-game check use those dimensions.

### Input and game-state protection

The game rejects commands with missing or extra fields, unknown orientations, non-integer coordinates, coordinates outside the selected board, and lines that have already been drawn. Rejected moves leave the board, scores, and active player unchanged. The shared rule validation checks a move before indexing line arrays, and `Board.add_line` repeats that guard for direct calls. A completed game rejects further moves through both the game and board interfaces.

## Design and modules

- `main.py` starts the application.
- `game.py` handles board-size selection, command parsing, player turns, scoring, and game-over output. `play_move` applies only validated moves.
- `rules.py` validates orientations, integer coordinates, bounds, repeated lines, and completed-game state. It also counts newly completed boxes.
- `board.py` stores horizontal and vertical lines and completed boxes, safely applies lines, displays the board, and checks whether all lines are drawn.
- `tests/test_game.py` contains deterministic automated tests using mocked input and captured output; it requires no third-party test framework.

## Run the automated tests

From the project folder, run:

```text
python -B -m unittest discover -s tests -v
```

The project uses only the Python standard library.
