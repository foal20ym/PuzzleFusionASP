from main import MainMenu
from tkinter import Tk
import unittest
# pylint: skip-file

class TestMainMenu(unittest.TestCase):
    def setUp(self):
        self.root = Tk()
        self.menu = MainMenu(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_menu_creation(self):
        buttons = [child for child in self.root.winfo_children() if isinstance(child, self.menu.canvas.__class__)]
        self.assertGreater(len(buttons), 0)

    def test_launch_sudoku(self):
        self.menu.launch_sudoku()
        self.assertNotIn(self.menu.canvas, self.root.winfo_children())

    def test_launch_minesweeper(self):
        self.menu.launch_minesweeper()
        self.assertNotIn(self.menu.canvas, self.root.winfo_children())

if __name__ == "__main__":
    unittest.main()