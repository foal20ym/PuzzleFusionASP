from apps.sudoku_app import SudokuApp
from tkinter import Tk
import unittest
from unittest.mock import MagicMock

class TestSudokuApp(unittest.TestCase):
    def setUp(self):
        self.root = Tk()
        self.app = SudokuApp(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_grid_creation(self):
        self.app.create_grid()
        self.assertEqual(len(self.app.entries), 9)
        self.assertEqual(len(self.app.entries[0]), 9)

    def test_generate_sudoku(self):
        self.app.generate_sudoku()
        filled_cells = sum(
            1 for row in self.app.entries for entry in row if entry.get()
        )
        self.assertGreater(filled_cells, 0)

    def test_validate_input(self):
        event = MagicMock(char="0", keysym="")
        self.assertEqual(self.app.validate_input(event, 0, 0), "break")

        event.char = "a"
        self.assertEqual(self.app.validate_input(event, 0, 0), "break")

        event.keysym = "BackSpace"
        self.assertIsNone(self.app.validate_input(event, 0, 0))

if __name__ == "__main__":
    unittest.main()
