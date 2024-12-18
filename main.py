import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from minesweeperApp import MinesweeperApp
from sudokuApp import SudokuApp

class WindowConfig:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    @staticmethod
    def from_geometry(geometry_str):
        size, position = geometry_str.split('+', 1)
        width, height = map(int, size.split('x'))
        x, y = map(int, position.split('+'))
        return WindowConfig(width, height, x, y)

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.is_fullscreen = False
        self.root.title("Main Menu")
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Set window size to 80% of screen size
        self.width = int(self.screen_width * 0.8)
        self.height = int(self.screen_height * 0.8)
        
        # Calculate center position
        x = (self.screen_width - self.width) // 2
        y = (self.screen_height - self.height) // 2
        
        # Set window size and position
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Load and resize background image
        self.bg_image = Image.open("BackgroundImages/cabinBackground.jpeg")
        self.bg_image = self.bg_image.resize((self.width, self.height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        
        # Create canvas with responsive sizing
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        
        # Bind resize event
        self.root.bind("<Configure>", self.on_resize)
        
        self.create_menu()
        
    def on_resize(self, event):
        # Get current fullscreen state
        new_fullscreen = self.root.attributes('-fullscreen')
        
        # Handle fullscreen toggle
        if new_fullscreen != self.is_fullscreen:
            if new_fullscreen:  # Entering fullscreen
                self.pre_fullscreen_geometry = self.root.geometry()
            else:  # Exiting fullscreen
                if self.pre_fullscreen_geometry:
                    self.root.after(100, lambda: self.root.geometry(self.pre_fullscreen_geometry))
            self.is_fullscreen = new_fullscreen
            return  # Skip any resize handling during toggle
            
        # Only handle actual window resizes
        if event.widget == self.root and \
           not self.is_fullscreen and \
           (self.width != event.width or self.height != event.height):
            self.width = event.width
            self.height = event.height
            
            # Resize background image
            self.bg_image = Image.open("BackgroundImages/cabinBackground.jpeg")
            self.bg_image = self.bg_image.resize((self.width, self.height), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            
            # Update canvas and redraw everything
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            self.create_menu()

    def create_menu(self):
        
        self.canvas.create_rectangle(self.width/2 - 100, 90, self.width/2 + 100, 110, fill="lightgray", outline="lightgray")
        self.canvas.create_text(self.width/2, 100, text="Select a game to play:", font=("Arial", 18), fill="black")
        
        sudoku_button = tk.Button(self.root, text="Play Sudoku", font=("Arial", 14), command=self.launch_sudoku, bg="white", highlightbackground="white", borderwidth=0, width=15)
        self.canvas.create_window(self.width/2, 200, window=sudoku_button)

        minesweeper_button = tk.Button(self.root, text="Play Minesweeper", font=("Arial", 14), command=self.launch_minesweeper, bg="white", highlightbackground="white", borderwidth=0, width=15)
        self.canvas.create_window(self.width/2, 300, window=minesweeper_button)

    def launch_sudoku(self):
        # Get current window state before destroying
        current_geometry = self.root.geometry()
        current_config = WindowConfig.from_geometry(current_geometry)
        
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.update_idletasks()
        
        # Pass current config to game
        SudokuApp(self.root, window_config=current_config)
        self.root.update()

    def launch_minesweeper(self):
        # Get current window state before destroying
        current_geometry = self.root.geometry()
        current_config = WindowConfig.from_geometry(current_geometry)
        
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.update_idletasks()
        
        # Pass current config to game
        MinesweeperApp(self.root, window_config=current_config)
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    MainMenu(root)
    root.mainloop()