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
        self.height = self.root.winfo_screenheight()
        # self.height = self.root.winfo_screenheight() // 2 # Use this when on Ubuntu and using Sway

        self.bg_image = Image.open("BackgroundImages/christmasTownImage.jpg")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.solution = None  # Will store the ASP solution
        self.solution_numbers = {}  # Will store number cells
        self.solution_mines = set()  # Will store mine locations
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
        button_commands = [self.solve, self.generate_hint, self.new_game, self.back_to_menu, self.reset]

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
    
    def solve_board(self):
        """Solve the entire board using ASP when starting a new game"""
        facts = []
        # Define grid size constants
        facts.append(f"#const r={self.grid_size}.")
        facts.append(f"#const c={self.grid_size}.")
        
        # Add known mine positions
        for row, col in self.mines:
            facts.append(f"mine({col},{row}).")
        
        # Add initial numbers
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if (row, col) not in self.mines:
                    count = self.count_adjacent_mines(row, col)
                    facts.append(f"number({col},{row},{count}).")
        
        solutions = self.asp_solver("\n".join(facts))
        
        if solutions and solutions[0]:
            self.solution = solutions[0]
            # Store solution in easy-to-use format
            self.solution_mines = set()
            self.solution_numbers = {}
            
            for symbol in self.solution:
                if str(symbol.name) == "mine":
                    col, row = symbol.arguments
                    self.solution_mines.add((row.number, col.number))
                elif str(symbol.name) == "number":
                    col, row, num = symbol.arguments
                    self.solution_numbers[(row.number, col.number)] = num.number

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
        # Define grid size constants
        facts.append(f"#const r={self.grid_size}.")
        facts.append(f"#const c={self.grid_size}.")
        
        # Add revealed numbers
        for cell in self.revealed:
            row, col = cell
            count = self.count_adjacent_mines(row, col)
            facts.append(f"number({col},{row},{count}).")  # Note: number(col,row,num) format
        
        return "\n".join(facts)

    def generate_hint(self):
        """Get next safe move from stored solution"""
        if not self.solution:
            messagebox.showinfo("Hint", "No solution available!")
            return
            
        # Look for an unrevealed safe cell
        for pos, num in self.solution_numbers.items():
            if pos not in self.revealed and pos not in self.mines:
                row, col = pos
                self.cells[row][col].config(bg="lightgreen")
                return
        
        messagebox.showinfo("Hint", "No more safe moves available!")

    def solve(self):
        """Reveal all safe cells using stored solution"""
        if not self.solution:
            messagebox.showinfo("Solver", "No solution available!")
            return
            
        # Place flags on all mines
        for row, col in self.solution_mines:
            if (row, col) not in self.flags:
                self.toggle_flag(row, col)
        
        # Reveal all safe cells
        for pos, num in self.solution_numbers.items():
            row, col = pos
            if pos not in self.revealed and pos not in self.mines:
                self.cell_clicked(row, col)

    def new_game(self):
        "new game"
        self.mines = set()
        self.revealed = set()
        self.flags = set()
        self.solution = None
        self.solution_numbers = {}
        self.solution_mines = set()
        
        # Reset grid
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.cells[row][col].config(text="", state="normal", bg="gray")
        
        # Place mines
        while len(self.mines) < self.num_mines:
            self.mines.add((randint(0, self.grid_size - 1), randint(0, self.grid_size - 1)))
        
        # Solve board
        self.solve_board()
        
    def reset(self):
        "reset"
        self.new_game()

    def back_to_menu(self):
        "back to menu"
        from main import MainMenu
        for widget in self.root.winfo_children():
            widget.destroy()
        MainMenu(self.root)
