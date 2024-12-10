% minesweeper.pl
% Jolyon Bloomfield February 2022
% https://blog.dodgyfysix.com, https://github.com/jolyonb/blog_puzzles
% Inputs:
% #const r=number of rows.
% #const c=number of columns.
% Clue entries:
% number(col, row, num).

% SOURCE: https://github.com/jolyonb/blog_puzzles/blob/main/solvers/asp/clingo/minesweeper.pl

% Initialization
% Define our indices
rows(0..r-1).  % Row entries, 0-indexed to align with python
cols(0..c-1).  % Column entries, 0-indexed to align with python
nums(0..8).  % Allowed numbers in a cell

% Create an index for all cells we can manipulate
excluded(-100000,-100000).  % Just in case nothing else is excluded
cell(C, R) :- rows(R), cols(C), not excluded(C, R).

% Processing
% Rule 1: All cells must contain one of a mine or a number from 0 to 8
{number(C, R, Z) : nums(Z) ; mine(C, R)} = 1 :- cell(C, R).

% Rule 2: Cells containing a number must have that many mines adjacent to them
{mine(Cadj, Radj) : adj(Cadj, Radj, C, R)} = N :- number(C, R, N).
% Adjacency helper, specifying if (Cadj, Radj) is adjacent to (C, R)
adj(Cadj, Radj, C, R) :- cell(C, R), cell(Cadj, Radj), |R-Radj|**2 + |C-Cadj|**2 <= 2, |R-Radj|**2 + |C-Cadj|**2 > 0.

#show mine/2.
#show number/3.