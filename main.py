import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from minesweeperApp import MinesweeperApp
from sudokuApp import SudokuApp

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Menu")
        #self.width = 896, self.height = 512, self.root.geometry("896x512")
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        geometryString = str(self.width) + "x" + str(self.height)
        self.root.geometry(geometryString)

        self.bg_image = Image.open("BackgroundImages/cabinBackground.jpeg")
        self.bg_image = self.bg_image.resize((self.width, self.height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.create_menu()

    def create_menu(self):
        # self.canvas.create_rectangle(self.width/2 - 100, 90, self.width/2 + 100, 110, fill="lightgray", outline="lightgray")
        # self.canvas.create_text(self.width/2, 100, text="Select a game to play:", font=("Arial", 18), fill="black")
        
        sudoku_button = tk.Button(self.root, text="Play Sudoku", font=("Arial", 14), command=self.launch_sudoku, bg="white", highlightbackground="white", borderwidth=0, width=15)
        self.canvas.create_window(self.width/2, 200, window=sudoku_button)

        ttt_button = tk.Button(self.root, text="Play Tic Tac Toe", font=("Arial", 14), command=self.launch_tic_tac_toe, bg="white", highlightbackground="white", borderwidth=0, width=15)
        self.canvas.create_window(self.width/2, 250, window=ttt_button)

        minesweeper_button = tk.Button(self.root, text="Play Minesweeper", font=("Arial", 14), command=self.launch_minesweeper, bg="white", highlightbackground="white", borderwidth=0, width=15)
        self.canvas.create_window(self.width/2, 300, window=minesweeper_button)

        # exit button
        exit_button = tk.Button(self.root, text="Exit", font=("Arial", 14), command=self.exit_app, bg="red", fg="white", highlightbackground="red", activebackground="red", borderwidth=0)
        self.canvas.create_window(self.width/2, 350, window=exit_button)

    def exit_app(self):
        self.root.quit()

    def launch_sudoku(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            self.root.update()
        self.root.update_idletasks()
        SudokuApp(self.root)
        self.root.update()

    def launch_tic_tac_toe(self):
        messagebox.showinfo("Tic Tac Toe", "Tic Tac Toe game coming soon!")

    def launch_minesweeper(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            self.root.update()
        self.root.update_idletasks()
        MinesweeperApp(self.root)
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    MainMenu(root)
    root.mainloop()
