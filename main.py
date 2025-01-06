"""
Main module
===========

This module is the main module of the application. It creates the main menu and launches the different games.

Authors: Alexander Forsanker, Ivo Östberg Nilsson, Joel Scarinius Stävmo, Linus Savinainen
Created: Monday January 6, 2025
"""
import tkinter as tk
from tkinter import messagebox
import platform
from PIL import Image, ImageTk
from minesweeper_app import MinesweeperApp
from sudoku_app import SudokuApp

if platform.system() == "Darwin":
    from tkmacosx import Button
else:
    Button = tk.Button

class MainMenu:
    """
    MainMenu Class
    --------------
    Provides a main menu GUI with options to launch different games or exit the application.
    """

    def __init__(self, root):
        """
        Initialize the main menu interface.

        Args:
            The __init__ function takes the root (tk.Tk) which is the tkinter window object as an arg.
        """
        self.root = root
        self.root.title("Main Menu")
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        geometry_string = str(self.width) + "x" + str(self.height)
        self.root.geometry(geometry_string)

        self.bg_image = Image.open("BackgroundImages/cabinBackground.jpeg")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.create_menu()

    def create_menu(self):
        """
        Create the main menu with buttons to navigate to games or exit the application.
        """
        sudoku_button = tk.Button(self.root, text="Play Sudoku", font=("Arial", 14),
            command=self.launch_sudoku, bg="white", highlightbackground="white", borderwidth=0, width=15)
        self.canvas.create_window(self.width/2, 200, window=sudoku_button)

        minesweeper_button = tk.Button(self.root, text="Play Minesweeper", font=("Arial", 14),
            command=self.launch_minesweeper, bg="white", highlightbackground="white", borderwidth=0, width=15)
        self.canvas.create_window(self.width/2, 250, window=minesweeper_button)

        exit_button = Button(self.root, text="Exit", font=("Arial", 14),
            command=self.exit_app, bg="red", fg="white", highlightbackground="red", activebackground="red", borderwidth=0)
        self.canvas.create_window(self.width/2, 300, window=exit_button)

    def exit_app(self):
        """
        Exit the application by closing the tkinter window. This will also stop the main loop and works by calling the quit method on the root window.
        """
        self.root.quit()

    def launch_sudoku(self):
        """
        Launch the Sudoku game application.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
            self.root.update()
        self.root.update_idletasks()
        SudokuApp(self.root)
        self.root.update()

    def launch_minesweeper(self):
        """
        Launch the Minesweeper game application.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
            self.root.update()
        self.root.update_idletasks()
        MinesweeperApp(self.root)
        self.root.update()

if __name__ == "__main__":
    tk_root = tk.Tk()
    MainMenu(tk_root)
    tk_root.mainloop()
