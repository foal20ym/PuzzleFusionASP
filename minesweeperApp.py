import tkinter as tk
from tkinter import messagebox
from random import sample, randint
from PIL import Image, ImageTk
import clingo

class MinesweeperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper Game")
        self.width = 896
        self.height = 512

        self.bg_image = Image.open("BackgroundImages/puzzleAppbackground.jpeg")
        self.bg_image = self.bg_image.resize((self.width, self.height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.grid_size = 10  # 10x10 grid
        self.num_mines = 10
        self.cell_size = 40
        self.cells = []
        self.mines = set()
        self.revealed = set()
        self.flags = set()

        self.create_grid()
        self.create_buttons()
        self.new_game()

    def create_grid(self):
        grid_size_width = 10 # 10x10 grid
        grid_size = 400
        cell_size = grid_size // grid_size_width
        start_x = (self.width - grid_size) // 2
        start_y = (self.height - grid_size) // 2

        for row in range(self.grid_size):
            row_cells = []
            for col in range(self.grid_size):
                button = tk.Button(self.root, width=2, height=1, command=lambda r=row, c=col: self.cell_clicked(r, c), justify='center')
                button.bind("<Button-3>", lambda event, r=row, c=col: self.toggle_flag(r, c))
                button.place(x=start_x + col * cell_size, y=start_y + row * cell_size, width=cell_size, height=cell_size)
                row_cells.append(button)
            self.cells.append(row_cells)

    def create_buttons(self, button_width=80, spacing=10):
        button_texts=["New Game", "Reset", "Back"]  
        button_commands = [self.new_game, self.reset, self.back_to_menu]
        
        button_height = 30
        grid_size = 400
        start_y = (self.height - grid_size) // 2
        y_position = start_y + grid_size + 1 # +1 är för spacing mellan grid och knappar

        if spacing is None:
            spacing = (self.width - (button_width * len(button_texts))) // (len(button_texts) + 1)

        total_width = (button_width * len(button_texts)) + (spacing * (len(button_texts) - 1))
        start_x = (self.width - total_width) // 2

        for i, (text, command) in enumerate(zip(button_texts, button_commands)):
            x_position = start_x + i * (button_width + spacing)
            button = tk.Button(self.root, text=text, command=command, width=10)
            button.place(x=x_position, y=y_position, width=button_width, height=button_height)

    def cell_clicked(self, row, col):
        if (row, col) in self.flags:
            return
        if (row, col) in self.mines:
            self.reveal_mines()
            messagebox.showerror("Game Over", "You clicked on a mine!")
            self.reset()
        else:
            self.reveal_cell(row, col)
            if len(self.revealed) == self.grid_size * self.grid_size - self.num_mines:
                messagebox.showinfo("Congratulations", "You won!")
                self.reset()

    def reveal_cell(self, row, col):
        if (row, col) in self.revealed:
            return
        self.revealed.add((row, col))
        self.cells[row][col].config(state="disabled", relief=tk.SUNKEN)
        mine_count = self.count_adjacent_mines(row, col)
        if mine_count > 0:
            self.cells[row][col].config(text=str(mine_count))
        else:
            for r in range(max(0, row-1), min(self.grid_size, row+2)):
                for c in range(max(0, col-1), min(self.grid_size, col+2)):
                    if (r, c) != (row, col):
                        self.reveal_cell(r, c)

    def count_adjacent_mines(self, row, col):
        count = 0
        for r in range(max(0, row-1), min(self.grid_size, row+2)):
            for c in range(max(0, col-1), min(self.grid_size, col+2)):
                if (r, c) in self.mines:
                    count += 1
        return count

    def toggle_flag(self, row, col):
        if (row, col) in self.revealed:
            return
        if (row, col) in self.flags:
            self.flags.remove((row, col))
            self.cells[row][col].config(text="")
        else:
            self.flags.add((row, col))
            self.cells[row][col].config(text="F")

    def reveal_mines(self):
        for mine in self.mines:
            self.cells[mine[0]][mine[1]].config(text="M", bg="red")

    def new_game(self):
        self.mines = set()
        self.revealed = set()
        self.flags = set()
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.cells[row][col].config(text="", state="normal", relief=tk.RAISED, bg="lightgray")
        while len(self.mines) < self.num_mines:
            self.mines.add((randint(0, self.grid_size-1), randint(0, self.grid_size-1)))

    def reset(self):
        self.new_game()

    def back_to_menu(self):
        from main import MainMenu
        for widget in self.root.winfo_children():
            widget.destroy()
            #self.root.update() # Kommentera ut för att få den roliga animationen :) 
        self.root.update_idletasks()
        MainMenu(self.root)
        self.root.update()
