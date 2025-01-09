from apps.minesweeper_app import MinesweeperApp
from tkinter import Tk
import unittest
from unittest.mock import patch

class TestMinesweeperApp(unittest.TestCase):
    def setUp(self):
        self.root = Tk()
        self.app = MinesweeperApp(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_grid_creation(self):
        self.app.create_grid()
        self.assertEqual(len(self.app.cells), self.app.grid_size)
        self.assertEqual(len(self.app.cells[0]), self.app.grid_size)

    def test_new_game_resets_state(self):
        self.app.new_game()
        self.assertFalse(self.app.game_over)
        self.assertEqual(len(self.app.mines), self.app.num_mines)
        self.assertEqual(len(self.app.revealed), 0)
        self.assertEqual(len(self.app.flags), 0)

    @patch('minesweeper_app.messagebox')
    def test_cell_clicked_game_over2(self, mock_messagebox):
        self.app.mines.add((0, 0))
        
        with patch.object(self.app, 'reset', return_value=None):
            self.app.cell_clicked(0, 0)
            self.assertTrue(self.app.game_over)
            mock_messagebox.showerror.assert_called_once_with("Game Over", "You clicked on a mine!")

    def test_toggle_flag(self):
        self.app.toggle_flag(0, 0)
        self.assertIn((0, 0), self.app.flags)
        self.app.toggle_flag(0, 0)
        self.assertNotIn((0, 0), self.app.flags)

if __name__ == "__main__":
    unittest.main()