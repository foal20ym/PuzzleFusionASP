# Puzzle Games with ASP Solvers

A collection of classic puzzle games (Sudoku and Minesweeper) enhanced with intelligent solving capabilities using Answer Set Programming (ASP). The games feature both manual play and automated assistance through Clingo ASP solvers.

## Features

- **Sudoku**
  - Interactive gameplay
  - Difficulty levels
  - Intelligent hints
  - Complete solution generation

- **Minesweeper**
  - Multiple difficulty settings
  - Safe move suggestions
  - Smart flagging system

## Prerequisites

- Python 3.8 or higher
- Clingo 5.5 or higher
- Tkinter (usually comes with Python)
- PIL (Python Imaging Library)

### Installation and running the application for Mac users:
1. Clone the repository and navigate to it:

    ```sh
    git clone https://github.com/foal20ym/PuzzleFusionASP.git
    ```

    ```sh
    cd PuzzleFusionASP
    ```

2. Install the required Python packages. To install all packages at once, run the following command in the terminal:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the program with the following command in the terminal:
    ```sh
    python3 main.py
    ```

### Installation for Linux/Windows

1. Clone the repository and navigate to it:

    ```sh
    git clone https://github.com/foal20ym/PuzzleFusionASP.git
    ```

    ```sh
    cd PuzzleFusionASP
    ```
2. You may need to activate a virtual enviroment. For Linux:
	```sh
	python -m venv ./venv
	source venv/bin/activate.<shell>
	```
	The "\<shell\>" depends on the shell you are using. For example, if you are using fish:
	```sh
	source venv/bin/activate.fish
	```
	With bash shell it simply is:
	 ```sh
	 source venv/bin/activate
	 ```

3. Install the required Python packages. To install all packages at once, run the following command in the terminal:

    ```sh
    make install
    ```

## Usage

### Run the application

```sh
make run
```

## Development Tools

### Check code style

```sh
make lint
```

### Run tests

```sh
make test
```
