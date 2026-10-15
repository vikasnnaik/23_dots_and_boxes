import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from board import Board
from game import DotsAndBoxes


def moves_to_complete(size):
    horizontal = [
        f"H {row} {col}"
        for row in range(size + 1)
        for col in range(size)
    ]
    vertical = [
        f"V {row} {col}"
        for row in range(size)
        for col in range(size + 1)
    ]
    return horizontal + vertical


class BoardSizeTests(unittest.TestCase):
    def test_each_supported_size_completes_a_full_game(self):
        for choice, size in (("1", 2), ("2", 3), ("3", 4)):
            with self.subTest(size=size):
                game = DotsAndBoxes()
                responses = [choice, *moves_to_complete(size)]
                output = StringIO()

                with patch("builtins.input", side_effect=responses), redirect_stdout(output):
                    game.run()

                self.assertEqual(game.board.rows, size)
                self.assertEqual(game.board.cols, size)
                self.assertEqual(len(game.board.horizontal), size + 1)
                self.assertEqual(len(game.board.horizontal[0]), size)
                self.assertEqual(len(game.board.vertical), size)
                self.assertEqual(len(game.board.vertical[0]), size + 1)
                self.assertTrue(game.board.is_complete())
                self.assertEqual(len(game.board.completed), size * size)
                self.assertEqual(game.scores, [(size // 2) * size, ((size + 1) // 2) * size])
                self.assertEqual(game.current, 1 if size % 2 else 0)
                game_output = output.getvalue()
                self.assertIn("Small (2x2 boxes)", game_output)
                self.assertIn("Medium (3x3 boxes)", game_output)
                self.assertIn("Large (4x4 boxes)", game_output)
                self.assertIn("Game over!", game_output)

    def test_invalid_size_retries_then_medium_game_runs(self):
        game = DotsAndBoxes()
        responses = ["not a size", "2", *moves_to_complete(3)]
        output = StringIO()

        with patch("builtins.input", side_effect=responses), redirect_stdout(output):
            game.run()

        self.assertIn("Invalid board size. Please choose 1, 2, or 3.", output.getvalue())
        self.assertEqual((game.board.rows, game.board.cols), (3, 3))
        self.assertTrue(game.board.is_complete())
        self.assertEqual(game.scores, [3, 6])

    def test_superscript_coordinate_is_rejected_without_state_change(self):
        game = DotsAndBoxes()
        responses = ["1", "H \N{SUPERSCRIPT TWO} 0", *moves_to_complete(2)]
        output = StringIO()
        calls = 0

        def next_input(_prompt):
            nonlocal calls
            if calls == 2:
                self.assertFalse(any(map(any, game.board.horizontal)))
                self.assertFalse(any(map(any, game.board.vertical)))
                self.assertEqual(game.board.completed, set())
                self.assertEqual(game.scores, [0, 0])
                self.assertEqual(game.current, 0)
            response = responses[calls]
            calls += 1
            return response

        with patch("builtins.input", side_effect=next_input), redirect_stdout(output):
            game.run()

        self.assertIn("Row and column must be valid integers.", output.getvalue())
        self.assertTrue(game.board.is_complete())
        self.assertEqual(game.scores, [2, 2])


class ValidationAndStateTests(unittest.TestCase):
    @staticmethod
    def snapshot(game):
        return (
            tuple(map(tuple, game.board.horizontal)),
            tuple(map(tuple, game.board.vertical)),
            frozenset(game.board.completed),
            tuple(game.scores),
            game.current,
        )

    def test_malformed_and_invalid_commands_leave_state_unchanged(self):
        game = DotsAndBoxes()
        invalid_commands = [
            "",
            "H 0",
            "H 0 0 extra",
            "X 0 0",
            "H nope 0",
            "H \N{SUPERSCRIPT TWO} 0",
            "H -1 0",
            "H 3 0",
            "V 0 3",
        ]
        responses = [
            "1",
            *invalid_commands,
            "H 0 0",
            "H 0 0",
            *(move for move in moves_to_complete(2) if move != "H 0 0"),
        ]
        initial_state = self.snapshot(game)
        after_first_move = (
            ((True, False), (False, False), (False, False)),
            ((False, False, False), (False, False, False)),
            frozenset(),
            (0, 0),
            1,
        )
        calls = 0
        output = StringIO()

        def next_input(_prompt):
            nonlocal calls
            if 1 <= calls <= len(invalid_commands) + 1:
                self.assertEqual(self.snapshot(game), initial_state)
            elif calls in (len(invalid_commands) + 2, len(invalid_commands) + 3):
                self.assertEqual(self.snapshot(game), after_first_move)
            response = responses[calls]
            calls += 1
            return response

        with patch("builtins.input", side_effect=next_input), redirect_stdout(output):
            game.run()

        text = output.getvalue()
        self.assertEqual(text.count("Invalid format."), 3)
        self.assertIn("Orientation must be H or V.", text)
        self.assertEqual(text.count("Row and column must be valid integers."), 2)
        self.assertEqual(text.count("Coordinates are outside the board."), 3)
        self.assertIn("That line has already been drawn.", text)
        self.assertTrue(game.board.is_complete())
        self.assertEqual(game.scores, [2, 2])

    def test_board_mutator_rejects_invalid_values_safely(self):
        board = Board(2, 2)
        initial = (
            tuple(map(tuple, board.horizontal)),
            tuple(map(tuple, board.vertical)),
            frozenset(board.completed),
        )
        output = StringIO()

        with redirect_stdout(output):
            self.assertFalse(board.add_line("H", -1, 0))
            self.assertFalse(board.add_line("H", 3, 0))
            self.assertFalse(board.add_line("V", 0, 3))
            self.assertFalse(board.add_line("X", 0, 0))
            self.assertFalse(board.add_line("H", "²", 0))

        self.assertEqual(
            (
                tuple(map(tuple, board.horizontal)),
                tuple(map(tuple, board.vertical)),
                frozenset(board.completed),
            ),
            initial,
        )

    def test_completing_a_box_scores_one_and_keeps_the_turn(self):
        game = DotsAndBoxes()
        game.board = Board(2, 2)

        output = StringIO()
        with redirect_stdout(output):
            for orientation, row, col in (
                ("H", 0, 0),
                ("H", 1, 0),
                ("V", 0, 0),
            ):
                self.assertTrue(game.play_move(orientation, row, col))

            self.assertEqual(game.current, 1)
            self.assertTrue(game.play_move("V", 0, 1))

        self.assertIn("Player 2 completed 1 box", output.getvalue())
        self.assertEqual(game.board.completed, {(0, 0)})
        self.assertEqual(game.scores, [0, 1])
        self.assertEqual(game.current, 1)

    def test_one_move_can_complete_multiple_boxes(self):
        game = DotsAndBoxes()
        game.board = Board(2, 2)

        for line in (
            ("H", 0, 0),
            ("H", 2, 0),
            ("V", 0, 0),
            ("V", 0, 1),
            ("V", 1, 0),
            ("V", 1, 1),
        ):
            self.assertTrue(game.board.add_line(*line))

        self.assertEqual(game.board.completed, set())
        output = StringIO()
        with redirect_stdout(output):
            self.assertTrue(game.play_move("H", 1, 0))

        self.assertEqual(game.board.completed, {(0, 0), (1, 0)})
        self.assertEqual(game.scores, [2, 0])
        self.assertEqual(game.current, 0)
        self.assertIn("Player 1 completed 2 box(es)", output.getvalue())
        self.assertFalse(game.board.is_complete())

    def test_completed_game_rejects_moves_through_game_and_board(self):
        game = DotsAndBoxes()
        responses = ["1", *moves_to_complete(2)]
        with patch("builtins.input", side_effect=responses), redirect_stdout(StringIO()):
            game.run()

        completed_state = self.snapshot(game)
        output = StringIO()
        with redirect_stdout(output):
            self.assertFalse(game.play_move("H", 0, 0))
            self.assertFalse(game.board.add_line("V", 0, 0))

        self.assertEqual(self.snapshot(game), completed_state)
        self.assertEqual(output.getvalue().count("Game is already complete"), 2)


if __name__ == "__main__":
    unittest.main()
