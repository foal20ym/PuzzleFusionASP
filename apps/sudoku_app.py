"""
Sudoku Game
===========

This code implements a Sudoku game using a graphical user interface (GUI) built with 
tkinter. The game makes use of Answer Set Programming (ASP) through Clingo to solve the sudoku.

Authors: Alexander Forsanker, Ivo Östberg Nilsson, Joel Scarinius Stävmo, Linus Savinainen
Created: Monday January 6, 2025
"""
from apps.sparql_app import get_answer
import tkinter as tk
from tkinter import messagebox, OptionMenu, StringVar, simpledialog
from random import sample
from PIL import Image, ImageTk
import clingo

class SudokuApp:
    """
    SudokuApp Class
    ---------------
    This class represents the Sudoku game using tkinter for GUI and Clingo for solving the grid.
    """
    def __init__(self, root):
        """
        Initializes the Sudoku game application.

        Args:
            The __init__ function takes the root (tk.Tk) which is the tkinter window object as an arg.
        """
        self.root = root
        self.root.title("Sudoku Game")
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        self.bg_image = Image.open("assets/christmasTownImage.jpg")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.difficulties = {
            "Easy": 3,
            "Medium": 5,
            "Hard": 6
        }
        self.difficulty_var = StringVar(self.root)
        self.difficulty_var.set("Easy")

        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.user_inputs = []
        self.score = 0
        self.create_grid()
        self.create_buttons()
        self.generate_sudoku()

        self.use_sparql_queries = False

    def create_grid(self):
        """
        Create the Sudoku grid.

        This method initializes a 9x9 grid of entry widgets for the Sudoku game.
        Each cell is represented by a tkinter "Entry widget", which is placed on the grid.
        Validation bindings are added to each entry to ensure valid input (validated by the validate_input function).
        """
        grid_size = 400
        cell_size = grid_size // 9
        start_x = (self.width - grid_size) // 2
        start_y = (self.height - grid_size) // 2

        for row in range(9):
            for col in range(9):
                entry = tk.Entry(self.root, width=2, font=('Arial', 18), justify='center')
                entry.place(x=start_x + col * cell_size, y=start_y + row * cell_size, width=cell_size, height=cell_size)
                self.entries[row][col] = entry
                entry.bind("<KeyPress>", lambda e, r=row, c=col: self.validate_input(e, r, c))

    def validate_input(self, event, row, col):
        """
        Validate input for Sudoku grid cells.

        This method guarantees that only valid input is allowed in the Sudoku grid cells.
        It blocks non-numeric input, prevents the entry of '0', and allows only single digits.
        It also allows backspace and delete keys for editing.

        Args:
            event (tkinter.Event): The event object containing information about the key press.
            row (int): The row index of the cell being validated.
            col (int): The column index of the cell being validated.

        Returns:
            The string 'break' to block the input. Or "None" of type None to allow the input.
        """
        if event.char.isdigit():
            if event.char == '0':
                return 'break'
            if self.entries[row][col].get():
                return 'break'
            return None
        if event.keysym in ('BackSpace', 'Delete'):
            return None
        return 'break'

    def track_user_input(self, row, col):
        """
        Track user input in the Sudoku grid.

        This method keeps track of the cells where the user has entered values.
        If a value is entered in a cell, the cell's coordinates are added to the user_inputs list.
        If a value is removed from a cell, the cell's coordinates are removed from the user_inputs list.

        Args:
            row (int): The row index of the cell.
            col (int): The column index of the cell.
        """
        value = self.entries[row][col].get()
        if value:
            self.user_inputs.append((row, col))
        else:
            self.user_inputs = [(r, c) for r, c in self.user_inputs if not (r == row and c == col)]

    def generate_sudoku(self):
        """
        Generate a new Sudoku puzzle.

        This method generates a new Sudoku puzzle based on the selected difficulty level.
        It creates a fully solved Sudoku board and then removes a certain number of cells
        to create the puzzle. The number of cells removed is based on the difficulty level.
        The generated puzzle is displayed in the grid, with the initial numbers set to read-only.
        """
        base = 3
        side = base * base

        def pattern(r, c):
            return (base * (r % base) + r // base + c) % side

        def shuffle(s):
            return sample(s, len(s))

        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, base * base + 1))

        board = [[nums[pattern(r, c)] for c in cols] for r in rows]

        empty_count_per_row = self.difficulties[self.difficulty_var.get()]
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
        """
        Solve the Sudoku puzzle.

        This method uses the ASP solver to find a solution for the current Sudoku puzzle.
        It retrieves the current game state as facts, solves the puzzle, and fills in the solution
        in the grid. If no solution exists, it shows an error message.
        """
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
        """
        Clear user inputs from the Sudoku grid.

        This method clears all user-entered values from the Sudoku grid,
        resetting the cells to their initial state.
        """
        for row, col in self.user_inputs:
            self.entries[row][col].config(state='normal')
            self.entries[row][col].delete(0, tk.END)
        self.user_inputs.clear()

    def new_game(self):
        """
        Start a new Sudoku game.

        This method clears the current grid, resets the game state by calling the "reset" function, 
        and generates a new Sudoku puzzle by calling the "generate_sudoku" function.        
        """
        for row in range(9):
            for col in range(9):
                self.entries[row][col].config(state='normal')
                self.entries[row][col].delete(0, tk.END)
        self.clear()
        self.generate_sudoku()

    def asp_solver(self, facts):
        """
        Solve the Sudoku puzzle using the Clingo ASP solver.

        This method creates a Clingo control object, loads the ASP program and facts,
        grounds the program, and solves it. The solutions are returned as a list of symbols.

        Args:
            facts (str): The facts representing the current game state.

        Returns:
            list: A list of solutions provided by the ASP solver.
        """
        ctl = clingo.Control()
        ctl.add("base", [], facts)
        with open("ASPSolvers/sudokuSolver.lp", encoding="UTF-8") as f:
            ctl.add("base", [], f.read())
        ctl.ground([("base", [])])

        models = []
        ctl.solve(on_model=lambda model: models.append(model.symbols(atoms=True)))
        return models

    def generate_hint_question(self):
        """
        Provides a hint to the user by asking a question from the YAGO knowledge base.

        This method attempts to retrieve a correct answer and a question. It then prompts the user
        with the question using a simple dialog box. If the user's answer matches any of the correct
        answers, a success message is shown and a hint is generated. If the answer is incorrect, an
        error message is displayed and no hint is provided.
        """

        # toggle to use or not to use the whole sparql thingy
        if not self.use_sparql_queries:
            self.generate_asp_hint()
            return
        
        try:
            correct_answer, question = get_answer()
        except Exception as err:
            messagebox.showerror("Error", f"Could not retrieve knowledge: {err}")
            return

        user_answer = simpledialog.askstring(
            "Knowledge Question",
            f"{question}\n"
        )

        if user_answer is None:
            return

        user_answer = str(user_answer).lower()
        correct_answer = [ans.lower() for ans in correct_answer]

        if user_answer in correct_answer:
            messagebox.showinfo("Correct!", "You got it right! Enjoy your hint.")
            self.generate_asp_hint()
        else:
            messagebox.showerror("Incorrect", "Sorry, that's not correct. No hint for you.")

    def generate_asp_hint(self):
        """
        Generate a hint for the next move in the Sudoku puzzle.

        This method uses the ASP solver to find a solution for the current Sudoku puzzle.
        It retrieves the current game state as facts, solves the puzzle, and provides a hint
        for the next move. If no solution exists, it shows an error message.
        """
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
        """
        Validate the current Sudoku puzzle with ASP.

        This method uses the ASP solver to check if the current Sudoku puzzle is solvable.
        If the puzzle is unsolvable, it shows an error message.
        """
        facts = self.get_current_facts()
        solutions = self.asp_solver(facts)
        if not solutions:
            messagebox.showerror("Invalid Move", "Puzzle is unsolvable!")

    def get_current_facts(self):
        """
        Generate facts representing the current game state.

        This method creates a list of facts based on the current state of the Sudoku grid,
        including the initial numbers entered by the user.

        Args:
            None

        Returns:
            str: A string containing the facts for the current game state.
        """
        facts = []
        for row in range(9):
            for col in range(9):
                value = self.entries[row][col].get()
                if value:
                    facts.append(f"initial({row + 1},{col + 1},{((row // 3) * 3 + col // 3)},{value}).")
        return "\n".join(facts)

    def create_buttons(self, button_width=80, spacing=10):
        """
        Creates control buttons for solving, hinting, starting a new game, and going back to the menu.

        Args:
            button_width (int): The width of each control button.
            spacing (int): The spacing between the control buttons.
        """
        button_texts = ["Solve", "Clear", "Hint", "New Game", "SPARQL?", "Back"]
        button_commands = [self.solve, self.clear, self.generate_hint_question, self.new_game, self.toggle_sparql, self.back_to_menu]

        button_height = 30
        grid_size = 400
        start_y = (self.height - grid_size) // 2
        y_position = start_y + grid_size + 1

        if spacing is None:
            spacing = (self.width - (button_width * len(button_texts))) // (len(button_texts) + 1)

        total_width = (button_width * len(button_texts)) + (spacing * (len(button_texts) - 1))
        start_x = (self.width - total_width) // 2

        for i, (text, command) in enumerate(zip(button_texts, button_commands)):
            x_position = start_x + i * (button_width + spacing)
            button = tk.Button(self.root, text=text, command=command, width=10)
            button.place(x=x_position, y=y_position, width=button_width, height=button_height)

        def update_difficulty(selected):
            self.difficulty_var.set(selected)
            self.create_grid()
            self.new_game()

        difficulty_menu = OptionMenu(self.root, self.difficulty_var, *self.difficulties.keys(), command=update_difficulty)
        difficulty_menu.config(fg="black")
        difficulty_menu.place(x=start_x, y=y_position + 40)

    def toggle_sparql(self):
        """
        Toggle the use of SPARQL queries.
    
        Toggles the use_sparql_queries boolean between True and False
        and shows feedback to user.
        """
        self.use_sparql_queries = not self.use_sparql_queries
        status = "ON" if self.use_sparql_queries else "OFF"
        messagebox.showinfo("SPARQL Toggle", f"SPARQL queries are now {status}.")

    def back_to_menu(self):
        """
        Return to the main menu.

        This method destroys the current game widgets and initializes the main menu.
        """
        from main import MainMenu
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.update_idletasks()
        MainMenu(self.root)
        self.root.update()
