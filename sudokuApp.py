import tkinter as tk
from tkinter import messagebox
from random import sample
from PIL import Image, ImageTk
import clingo

class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Game")
        #self.width = 896
        #self.height = 512
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        self.bg_image = Image.open("BackgroundImages/christmasTownImage.jpg")
        self.bg_image = self.bg_image.resize((self.width, self.height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.user_inputs = []
        self.score = 0
        self.create_grid()
        self.create_buttons()
        self.create_scoreboard()
        self.generate_sudoku()

    def create_scoreboard(self):
        self.score_label = tk.Label(self.root, text=f"Score: {self.score}", font=("Arial", 14), bg="black")
        self.canvas.create_window(50, 20, window=self.score_label)

    def update_score(self, points):
        self.score += points
        self.score_label.config(text=f"Score: {self.score}")

    def create_grid(self):
        grid_size = 400
        cell_size = grid_size // 9
        start_x = (self.width - grid_size) // 2
        start_y = (self.height - grid_size) // 2

        for row in range(9):
            for col in range(9):
                entry = tk.Entry(self.root, width=2, font=('Arial', 18), justify='center')
                entry.place(x=start_x + col * cell_size, y=start_y + row * cell_size, width=cell_size, height=cell_size)
                self.entries[row][col] = entry
                # Add validation bindings
                entry.bind("<KeyPress>", lambda e, r=row, c=col: self.validate_input(e, r, c))

    def validate_input(self, event, row, col):
        # Block non-numeric input
        if event.char.isdigit():
            if event.char == '0':
                return 'break'
            # Allow only single digit
            if self.entries[row][col].get():
                return 'break'
            return
        # Allow backspace/delete
        elif event.keysym in ('BackSpace', 'Delete'):
            return
        return 'break'

    def track_user_input(self, row, col):
        value = self.entries[row][col].get()
        if value:
            self.user_inputs.append((row, col))
        else:
            self.user_inputs = [(r, c) for r, c in self.user_inputs if not (r == row and c == col)]

    def generate_sudoku(self):
        base = 3
        side = base * base

        def pattern(r, c): 
            return (base * (r % base) + r // base + c) % side

        def shuffle(s): 
            return sample(s, len(s)) 

        rBase = range(base) 
        rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)] 
        cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
        nums = shuffle(range(1, base * base + 1))

        board = [[nums[pattern(r, c)] for c in cols] for r in rows]

        empty_count_per_row = (side // 2) + 1
        for row in range(9):
            empty_positions = sample(range(9), empty_count_per_row)
            for col in empty_positions:
                board[row][col] = 0

        for row in range(9):
            for col in range(9):
                if board[row][col] != 0:
                    self.entries[row][col].insert(0, board[row][col])
                    self.entries[row][col].config(state='readonly')

    def solve(self):
        messagebox.showinfo("Solve", "Solve button clicked")
        facts = self.get_current_facts()
        solutions = self.asp_solver(facts)
        
        if not solutions:
            messagebox.showerror("No solution exists!")
            return

        solution = solutions[0]
        for symbol in solution:
            if symbol.name == "sudoku" and len(symbol.arguments) == 3:
                x, y, v = symbol.arguments
                row, col, value = int(x.number), int(y.number), int(v.number)

                if not self.entries[row - 1][col - 1].get():
                    self.entries[row - 1][col - 1].insert(0, value)
                    self.entries[row - 1][col - 1].config(state='readonly')
                    self.user_inputs.append((row - 1, col - 1))

    def clear(self):
        for row, col in self.user_inputs:
            self.entries[row][col].config(state='normal')
            self.entries[row][col].delete(0, tk.END)
        self.user_inputs.clear()

    def new_game(self):
        for row in range(9):
            for col in range(9):
                self.entries[row][col].config(state='normal')
                self.entries[row][col].delete(0, tk.END)
        self.clear()
        self.generate_sudoku()
    
    def asp_solver(self, facts):
        ctl = clingo.Control()
        ctl.add("base", [], facts)
        with open("sudokuSolver.lp") as f:
            ctl.add("base", [], f.read())
        ctl.ground([("base", [])])

        models = []
        ctl.solve(on_model=lambda model: models.append(model.symbols(atoms=True)))
        return models

    def generate_hint(self):
        facts = self.get_current_facts()
        solutions = self.asp_solver(facts)
        
        if not solutions:
            messagebox.showerror("Hint Error", "No solution exists!")
            return

        solution = solutions[0]
        for symbol in solution:
            if symbol.name == "sudoku" and len(symbol.arguments) == 3:
                x, y, v = symbol.arguments
                row, col, value = int(x.number), int(y.number), int(v.number)

                if not self.entries[row - 1][col - 1].get():
                    hint_message = f"Suggested number: {value} at row {row}, column {col}"
                    messagebox.showinfo("Hint", hint_message)
                    self.entries[row - 1][col - 1].insert(0, value)
                    self.entries[row - 1][col - 1].config(state='readonly')
                    self.user_inputs.append((row - 1, col - 1))
                    return

        messagebox.showinfo("Hint", "No hints available!")

    def validate_puzzle(self):
        facts = self.get_current_facts()
        solutions = self.asp_solver(facts)
        if not solutions:
            messagebox.showerror("Invalid Move", "Puzzle is unsolvable!")

    def get_current_facts(self):
        facts = []
        for row in range(9):
            for col in range(9):
                value = self.entries[row][col].get()
                if value:
                    facts.append(f"initial({row + 1},{col + 1},{((row // 3) * 3 + col // 3)},{value}).")
        return "\n".join(facts)

    def create_buttons(self, button_width=80, spacing=10):
        button_texts = ["Solve", "Clear", "Hint", "New Game", "Back"]
        button_commands = [self.solve, self.clear, self.generate_hint, self.new_game, self.back_to_menu]
        
        button_height = 30
        grid_size = 400
        cell_size = grid_size // 9
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

    def back_to_menu(self):
        from main import MainMenu
        for widget in self.root.winfo_children():
            widget.destroy()
            # self.root.update() # Kommentera ut för att få den roliga animationen :)
        self.root.update_idletasks()
        MainMenu(self.root)
        self.root.update()
