"""
Minesweeper module
"""
import tkinter as tk
from tkinter import messagebox
from random import randint
import platform
from PIL import Image, ImageTk
import clingo

# Check if MacOS is used and changes to tkmacosx if that is the case
is_macos = platform.system() == "Darwin"
if is_macos:
    from tkmacosx import Button
else:
    Button = tk.Button

class MinesweeperApp:
    "Minesweeper app"
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper Game")
        self.width = self.root.winfo_screenwidth()
        # self.height = self.root.winfo_screenheight()
        self.height = self.root.winfo_screenheight() // 2 # Use this when on Ubuntu and using Sway

        self.bg_image = Image.open("BackgroundImages/christmasTownImage.jpg")
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
        self.asp_rules = "minesweeperSolver.lp"

        self.create_grid()
        self.create_buttons()
        self.new_game()

    def create_grid(self):
        "create a grid"
        grid_size = 400
        cell_size = grid_size // self.grid_size
        start_x = (self.width - grid_size) // 2
        start_y = (self.height - grid_size) // 2

        for row in range(self.grid_size):
            row_cells = []
            for col in range(self.grid_size):
                button = Button(
                    self.root,
                    text="",
                    bg="lightgray",
                    fg="black",
                    width=40,
                    height=40,
                    command=lambda r=row, c=col: self.cell_clicked(r, c),
                )
                button.bind("<Button-3>", lambda event, r=row, c=col: self.toggle_flag(r, c))
                button.place(
                    x=start_x + col * cell_size,
                    y=start_y + row * cell_size,
                    width=cell_size,
                    height=cell_size,
                )
                row_cells.append(button)
            self.cells.append(row_cells)

    def create_buttons(self, button_width=80, spacing=10):
        "create buttons"
        button_texts = ["Solve", "Hint", "New Game", "Back"]
        button_commands = [self.solve, self.generate_hint, self.new_game, self.back_to_menu]

        button_height = 30
        grid_size = 400
        start_y = (self.height - grid_size) // 2
        y_position = start_y + grid_size + 10  # Space between grid and buttons

        total_width = (button_width * len(button_texts)) + (spacing * (len(button_texts) - 1))
        start_x = (self.width - total_width) // 2

        for i, (text, command) in enumerate(zip(button_texts, button_commands)):
            x_position = start_x + i * (button_width + spacing)
            button = Button(self.root, text=text, command=command, bg="white", fg="black")
            button.place(x=x_position, y=y_position, width=button_width, height=button_height)

    def cell_clicked(self, row, col):
        "cell clicked"
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
        "reveal cell"
        if (row, col) in self.revealed:
            return
        self.revealed.add((row, col))
        self.cells[row][col].config(state="disabled", bg="lightgray")
        mine_count = self.count_adjacent_mines(row, col)
        if mine_count > 0:
            self.cells[row][col].config(text=str(mine_count), bg="lightgray")
        else:
            for r in range(max(0, row - 1), min(self.grid_size, row + 2)):
                for c in range(max(0, col - 1), min(self.grid_size, col + 2)):
                    if (r, c) != (row, col):
                        self.reveal_cell(r, c)
                        self.cells[row][col].config(bg="lightgray")

    def count_adjacent_mines(self, row, col):
        "count adjacent mines"
        count = 0
        for r in range(max(0, row - 1), min(self.grid_size, row + 2)):
            for c in range(max(0, col - 1), min(self.grid_size, col + 2)):
                if (r, c) in self.mines:
                    count += 1
        return count

    def toggle_flag(self, row, col):
        "toggle flag"
        if (row, col) in self.revealed:
            return
        if (row, col) in self.flags:
            self.flags.remove((row, col))
            self.cells[row][col].config(text="")
        else:
            self.flags.add((row, col))
            self.cells[row][col].config(text="F")

    def reveal_mines(self):
        "reveal mines"
        for mine in self.mines:
            self.cells[mine[0]][mine[1]].config(text="M", bg="red")

    def asp_solver(self, facts):
        """Solve using Clingo ASP solver"""
        try:
            # Create control object
            ctl = clingo.Control()
            
            # Load ASP program
            with open(self.asp_rules, 'r', encoding='utf-8') as f:
                program = f.read()
            
            # Add program and facts
            ctl.add("base", [], program)
            ctl.add("base", [], facts)
            
            # Ground and solve
            ctl.ground([("base", [])])
            solutions = []
            
            def on_model(model):
                solutions.append(model.symbols(shown=True))
            
            ctl.solve(on_model=on_model)
            return solutions
            
        except Exception as e:
            messagebox.showerror("Error", f"ASP Solver error: {str(e)}")
            return []
            
    def get_current_facts(self):
        """Generate facts for current game state"""
        facts = []
        # Add board size
        facts.append(f"boardsize({self.grid_size}).")
        # Add known mines
        for mine in self.mines:
            facts.append(f"mine({mine[0]+1},{mine[1]+1}).")
        # Add revealed cells
        for cell in self.revealed:
            count = self.count_adjacent_mines(cell[0], cell[1])
            facts.append(f"revealed({cell[0]+1},{cell[1]+1},{count}).")
        # Add flagged cells
        for flag in self.flags:
            facts.append(f"flagged({flag[0]+1},{flag[1]+1}).")
        return "\n".join(facts)

    def generate_hint(self):
        """Get next safe move from ASP solver"""
        facts = self.get_current_facts()
        solutions = self.asp_solver(facts)
        
        if not solutions or not solutions[0]:
            messagebox.showinfo("Hint", "No safe moves found!")
            return
            
        solution = solutions[0]
        # Debug print
        print("ASP Solution:", solution)
        
        for symbol in solution:
            if str(symbol.name) != "mine":
                try:
                    row, col = symbol.arguments
                    # Convert from 1-based to 0-based indexing
                    row_idx = row.number - 1
                    col_idx = col.number - 1
                    # Verify indices are valid
                    if 0 <= row_idx < self.grid_size and 0 <= col_idx < self.grid_size:
                        hint_message = f"Safe cell at row {row_idx + 1}, column {col_idx + 1}"
                        messagebox.showinfo("Hint", hint_message)
                        # Highlight the safe cell
                        self.cells[row_idx][col_idx].config(bg="lightgreen")
                        return
                except Exception as e:
                    print(f"Error processing hint: {e}")
                    continue
        
        messagebox.showinfo("Hint", "Could not determine a safe move")

    def solve(self):
        """Solve entire game using ASP"""
        facts = self.get_current_facts()
        solutions = self.asp_solver(facts)
        
        if not solutions:
            messagebox.showinfo("Solver", "No solution found!")
            return
            
        solution = solutions[0]
        for symbol in solution:
            if symbol.name == "mine":
                row, col = symbol.arguments
                # Mark mines with flags
                self.toggle_flag(row.number-1, col.number-1)
            elif symbol.name == "safe":
                row, col = symbol.arguments
                # Reveal safe cells
                self.cell_clicked(row.number-1, col.number-1)

    def new_game(self):
        "new game"
        self.mines = set()
        self.revealed = set()
        self.flags = set()
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.cells[row][col].config(text="", state="normal", bg="gray")
        while len(self.mines) < self.num_mines:
            self.mines.add((randint(0, self.grid_size - 1), randint(0, self.grid_size - 1)))

    def back_to_menu(self):
        "back to menu"
        from main import MainMenu
        for widget in self.root.winfo_children():
            widget.destroy()
        MainMenu(self.root)
