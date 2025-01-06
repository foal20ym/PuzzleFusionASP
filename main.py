"""
main module
"""
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from minesweeper_app import MinesweeperApp
from sudoku_app import SudokuApp

class MainMenu:
    "Main menu"
    def __init__(self, root):
        "init"
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
        "create menu"
        sudoku_button = tk.Button(self.root, text="Play Sudoku", font=("Arial", 14),
            command=self.launch_sudoku, bg="white", highlightbackground="white", borderwidth=0, width=15)
        self.canvas.create_window(self.width/2, 200, window=sudoku_button)

        ttt_button = tk.Button(self.root, text="Play Tic Tac Toe", font=("Arial", 14),
            command=self.launch_tic_tac_toe, bg="white", highlightbackground="white", borderwidth=0, width=15)
        self.canvas.create_window(self.width/2, 250, window=ttt_button)

        minesweeper_button = tk.Button(self.root, text="Play Minesweeper", font=("Arial", 14),
            command=self.launch_minesweeper, bg="white", highlightbackground="white", borderwidth=0, width=15)
        self.canvas.create_window(self.width/2, 300, window=minesweeper_button)

        # exit button
        exit_button = tk.Button(self.root, text="Exit", font=("Arial", 14),
            command=self.exit_app, bg="red", fg="white", highlightbackground="red", activebackground="red", borderwidth=0)
        self.canvas.create_window(self.width/2, 350, window=exit_button)

    def exit_app(self):
        "exit the whole app"
        self.root.quit()

    def launch_sudoku(self):
        "launch sudoku"
        for widget in self.root.winfo_children():
            widget.destroy()
            self.root.update()
        self.root.update_idletasks()
        SudokuApp(self.root)
        self.root.update()

    def launch_tic_tac_toe(self):
        "launch tic tac toe"
        messagebox.showinfo("Tic Tac Toe", "Tic Tac Toe game coming soon!")

    def launch_minesweeper(self):
        "launch minesweeper"
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
