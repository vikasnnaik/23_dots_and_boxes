def valid_move(board, orientation, row, col):
    return move_error(board, orientation, row, col) is None


def move_error(board, orientation, row, col):
    if board.is_complete():
        return "Game is already complete; no more moves can be made."
    if not isinstance(orientation, str) or orientation not in {"H", "V"}:
        return "Orientation must be H or V."
    if type(row) is not int or type(col) is not int:
        return "Row and column must be valid integers."

    if orientation == "H":
        if not (0 <= row <= board.rows and 0 <= col < board.cols):
            return "Coordinates are outside the board."
        if board.horizontal[row][col]:
            return "That line has already been drawn."
    else:
        if not (0 <= row < board.rows and 0 <= col <= board.cols):
            return "Coordinates are outside the board."
        if board.vertical[row][col]:
            return "That line has already been drawn."

    return None


def completed_boxes(board, before):
    return len(board.completed - before)
