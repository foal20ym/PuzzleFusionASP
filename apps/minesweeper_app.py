"""
Minesweeper Game
================

This code implements a Minesweeper game using a graphical user interface (GUI) built with 
tkinter. The game makes use of Answer Set Programming (ASP) through Clingo to solve the board.

Authors: Alexander Forsanker, Ivo Östberg Nilsson, Joel Scarinius Stävmo, Linus Savinainen
Created: Monday January 6, 2025
"""
from apps.sparql_app import get_answer
import tkinter as tk
from tkinter import messagebox, OptionMenu, StringVar, simpledialog
from random import randint
import platform
from PIL import Image, ImageTk
import clingo

if platform.system() == "Darwin":
    from tkmacosx import Button
else:
    Button = tk.Button

class MinesweeperApp:
    """
    MinesweeperApp Class
    --------------------
    This class represents the Minesweeper game using tkinter for GUI and Clingo for solving the board.
    """

    def __init__(self, root):
        """
        Initializes the Minesweeper game application.

        Args:
            The __init__ function takes the root (tk.Tk) which is the tkinter window object as an arg.
        """
        self.root = root
        self.root.title("Minesweeper Game")
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        self.bg_image = Image.open("assets/christmasTownImage.jpg")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.difficulties = {
            "Easy": (8, 10),
            "Medium": (10, 30),
            "Hard": (12, 50)
        }
        self.difficulty_var = StringVar(self.root)
        self.difficulty_var.set("Easy")
        self.grid_size, self.num_mines = self.difficulties[self.difficulty_var.get()]

        self.game_over = False
        self.solution = None
        self.solution_numbers = {}
        self.solution_mines = set()
        self.cell_size = 40
        self.cells = []
        self.mines = set()
        self.revealed = set()
        self.flags = set()
        self.asp_rules = "ASPSolvers/minesweeperSolver.lp"

        self.create_grid()
        self.create_buttons()
        self.new_game()

        self.use_sparql_queries = False

    def create_grid(self):
        """
        Creates the game grid with buttons representing cells.

        This function clears any existing grid and recreates it based on the current grid size.
        """
        for row_cells in self.cells:
            for button in row_cells:
                button.destroy()
        self.cells = []

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
        """
        Creates control buttons for solving, hinting, starting a new game, and going back to the menu.

        Args:
            button_width (int): The width of each control button.
            spacing (int): The spacing between the control buttons.
        """
        button_texts = ["Solve", "Hint", "New Game", "SPARQL?", "Back"]
        button_commands = [self.solve, self.generate_hint_question, self.new_game, self.toggle_sparql, self.back_to_menu]

        button_height = 30
        grid_size = 400
        start_y = (self.height - grid_size) // 2
        y_position = start_y + grid_size + 10

        total_width = (button_width * len(button_texts)) + (spacing * (len(button_texts) - 1))
        start_x = (self.width - total_width) // 2

        def update_difficulty(selected):
            """
            Update the game difficulty.

            This method sets the difficulty level based on the selected option,
            updates the grid size and number of mines accordingly, recreates the grid,
            and restarts the game with the new difficulty settings.

            Args:
                selected (str): The selected difficulty level.
            """
            self.difficulty_var.set(selected)
            self.grid_size, self.num_mines = self.difficulties[self.difficulty_var.get()]
            self.create_grid()
            self.new_game()

        difficulty_menu = OptionMenu(self.root, self.difficulty_var, *self.difficulties.keys(), command=update_difficulty)
        difficulty_menu.config(bg="white", fg="black")
        difficulty_menu.place(x=start_x, y=y_position + 40)

        for i, (text, command) in enumerate(zip(button_texts, button_commands)):
            x_position = start_x + i * (button_width + spacing)
            button = Button(self.root, text=text, command=command, bg="white", fg="black")
            button.place(x=x_position, y=y_position, width=button_width, height=button_height)

    def toggle_sparql(self):
            """
            Toggle the use of SPARQL queries.
        
            Toggles the use_sparql_queries boolean between True and False
            and shows feedback to user.
            """
            self.use_sparql_queries = not self.use_sparql_queries
            status = "ON" if self.use_sparql_queries else "OFF"
            messagebox.showinfo("SPARQL Toggle", f"SPARQL queries are now {status}.")

    def solve_board(self):
        """
        Solves the entire board using Answer Set Programming (ASP) when starting a new game.
        """
        facts = []
        facts.append(f"#const r={self.grid_size}.")
        facts.append(f"#const c={self.grid_size}.")

        for row, col in self.mines:
            facts.append(f"mine({col},{row}).")

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if (row, col) not in self.mines:
                    count = self.count_adjacent_mines(row, col)
                    facts.append(f"number({col},{row},{count}).")

        solutions = self.asp_solver("\n".join(facts))

        if solutions and solutions[0]:
            self.solution = solutions[0]
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
        """
        Handles the event when a cell is clicked.

        Args:
            row (int): The row index of the clicked cell.
            col (int): The column index of the clicked cell.
        """
        if self.game_over or (row, col) in self.flags:
            return
        if (row, col) in self.mines:
            self.reveal_mines()
            messagebox.showerror("Game Over", "You clicked on a mine!")
            self.game_over = True
        else:
            self.reveal_cell(row, col)
            if len(self.revealed) == self.grid_size * self.grid_size - self.num_mines:
                messagebox.showinfo("Congratulations", "You won!")
                self.game_over = True
        if self.game_over:
            self.reveal_mines()
            for pos, num in self.solution_numbers.items():
                row, col = pos
                self.reveal_cell(row, col)

    def reveal_cell(self, row, col):
        """
        Reveals a cell by updating its state and displaying the adjacent mine count.

        Args:
            row (int): The row index of the cell.
            col (int): The column index of the cell.
        """
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
        """
        Counts the number of adjacent mines for a given cell.

        Args:
            row (int): The row index of the cell.
            col (int): The column index of the cell.

        Returns:
            int: The number of adjacent mines.
        """
        count = 0
        for r in range(max(0, row - 1), min(self.grid_size, row + 2)):
            for c in range(max(0, col - 1), min(self.grid_size, col + 2)):
                if (r, c) in self.mines:
                    count += 1
        return count

    def toggle_flag(self, row, col):
        """
        Toggles a flag on or off for a given cell.

        Args:
            row (int): The row index of the cell.
            col (int): The col index of the cell.
        """
        if (row, col) in self.revealed:
            return
        if (row, col) in self.flags:
            self.flags.remove((row, col))
            self.cells[row][col].config(text="")
        else:
            self.flags.add((row, col))
            self.cells[row][col].config(text="F", bg="red")

    def reveal_mines(self):
        """
        Reveal all mines on the grid.

        This method iterates through all the mine locations and updates the 
        corresponding grid cells to display a mine symbol ('M') with a red background.
        """
        for mine in self.mines:
            self.cells[mine[0]][mine[1]].config(text="M", bg="red")

    def asp_solver(self, facts):
        """
        Solve the Minesweeper puzzle using the Clingo ASP solver.

        This method creates a Clingo control object, loads the ASP program and facts,
        grounds the program, and solves it. The solutions are then returned ad a list of symbols.

        Args:
            facts (str): The facts representing the current game state.

        Returns:
            list: A list of solutions provided by the ASP solver.
        """
        try:
            ctl = clingo.Control()

            with open(self.asp_rules, 'r', encoding='utf-8') as f:
                program = f.read()

            ctl.add("base", [], program)
            ctl.add("base", [], facts)

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
        """
        Generate facts representing the current game state.

        This method creates a list of facts based on the current state of the game,
        including the grid size and the numbers revealed on the grid.

        Returns:
            str: A string containing the facts for the current game state.
        """
        facts = []
        facts.append(f"#const r={self.grid_size}.")
        facts.append(f"#const c={self.grid_size}.")

        for cell in self.revealed:
            row, col = cell
            count = self.count_adjacent_mines(row, col)
            facts.append(f"number({col},{row},{count}).")

        return "\n".join(facts)
    
    def generate_hint_question(self):
            """
            Provides a hint to the user by asking a question from the YAGO knowledge base.

            This method attempts to retrieve a correct answer and a question. It then prompts the user
            with the question using a simple dialog box. If the user's answer matches any of the correct
            answers, a success message is shown and a hint is generated. If the answer is incorrect, an
            error message is displayed and no hint is provided.
            """

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
        Provide a hint for the next safe move.

        This method highlights the next safe cell to reveal based on the stored solution.
        If no solution is available or no safe moves are left, it shows a message indicating that no more moves are available.
        """
        if not self.solution:
            messagebox.showinfo("Hint", "No solution available!")
            return

        for pos, num in self.solution_numbers.items():
            if pos not in self.revealed and pos not in self.mines:
                row, col = pos
                self.cells[row][col].config(bg="lightgreen")
                return

        messagebox.showinfo("Hint", "No more safe moves available!")

    def solve(self):
        """
        Reveal all safe cells and flag all mines using the stored solution.

        This method uses the stored solution to place flags on all mines and reveal all safe cells.
        If no solution is available, it shows a message saying that. If the game is solved, it shows a congratulatory message.
        """
        if not self.solution:
            messagebox.showinfo("Solver", "No solution available!")
            return

        for row, col in self.solution_mines:
            if (row, col) not in self.flags:
                self.flags.add((row, col))
                self.cells[row][col].config(text="F", bg="red")

        for pos, num in self.solution_numbers.items():
            row, col = pos
            self.reveal_cell(row, col)

    def new_game(self):
        """
        Start a new game.

        This method resets the game state, clears the grid, places new mines, and solves the board.
        """
        self.mines = set()
        self.revealed = set()
        self.flags = set()
        self.solution = None
        self.solution_numbers = {}
        self.solution_mines = set()
        self.game_over = False

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.cells[row][col].config(text="", state="normal", bg="gray")

        while len(self.mines) < self.num_mines:
            self.mines.add((randint(0, self.grid_size - 1), randint(0, self.grid_size - 1)))

        self.solve_board()

    def reset(self):
        """
        Reset the game.

        This method resets the game and starts a new one by calling the new_game method.
        """
        self.new_game()

    def back_to_menu(self):
        """
        Return to the main menu.

        This method destroys the current game widgets and initializes the main menu.
        """
        from main import MainMenu
        for widget in self.root.winfo_children():
            widget.destroy()
        MainMenu(self.root)
