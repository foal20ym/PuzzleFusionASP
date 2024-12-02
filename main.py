import tkinter as tk
from tkinter import messagebox
from random import sample
import clingo

class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Game")
        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.create_grid()
        self.create_buttons()
        self.generate_sudoku()

    def create_grid(self):
        for row in range(9):
            for col in range(9):
                entry = tk.Entry(self.root, width=2, font=('Arial', 18), justify='center')
                entry.grid(row=row, column=col, padx=5, pady=5)
                self.entries[row][col] = entry

    def create_buttons(self):
        solve_button = tk.Button(self.root, text="Solve", command=self.solve)
        solve_button.grid(row=9, column=0, columnspan=5, pady=10)
        
        clear_button = tk.Button(self.root, text="Clear", command=self.clear)
        clear_button.grid(row=9, column=4, columnspan=5, pady=10)

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

        empty_count_per_row = (side // 2) + 1 # Ändra denna raden för att ändra antalet tomma rutor
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
        # Placeholder for solve functionality
        messagebox.showinfo("Solve", "Solve button clicked")

        # Hämta ASP facts och lösningarna som finns
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

    def clear(self):
        for row in range(9):
            for col in range(9):
                self.entries[row][col].config(state='normal')
                self.entries[row][col].delete(0, tk.END)
    
    def asp_solver(self, facts):
        ctl = clingo.Control()
        ctl.add("base", [], facts)
        with open("sudokuSolver.lp") as f: # Läser sudokuSolver.lp filen som innehåller ASP lösaren för Sudoku
            ctl.add("base", [], f.read())
        ctl.ground([("base", [])])

        models = []
        ctl.solve(on_model=lambda model: models.append(model.symbols(atoms=True)))
        return models

    def generate_hint(self):

        # Hämta ASP facts och lösningarna som finns
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

    def create_buttons(self):
        solve_button = tk.Button(self.root, text="Solve", command=self.solve)
        solve_button.grid(row=9, column=0, columnspan=3, pady=10)

        clear_button = tk.Button(self.root, text="Clear", command=self.clear)
        clear_button.grid(row=9, column=3, columnspan=3, pady=10)

        hint_button = tk.Button(self.root, text="Hint", command=self.generate_hint)
        hint_button.grid(row=9, column=6, columnspan=3, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()