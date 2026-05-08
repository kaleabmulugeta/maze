Maze Generator and Solver - CG Assignment 1
===========================================

A Python + Pygame program that generates and solves mazes using a stack-based
DFS "mouse" algorithm for carving and BFS for solving.

How to run
----------
pip install pygame
python .\maze.py

Controls
--------
- Q or Esc: quit

How it works
------------

Data structure
--------------
The maze is stored using two 2D arrays:

python:
northWall[ROWS + 1][COLS]  # True = top wall of cell is intact
eastWall[ROWS][COLS + 1]   # True = right wall of cell is intact

Row 0 of northWall is a phantom row below the visible maze. Its north walls
form the bottom edge. This lets every wall be represented consistently.

Generating the maze (stack-based DFS mouse)
-------------------------------------------
1. Start with all walls intact (grid only).
2. Place a mouse at a random cell and mark it visited.
3. The mouse checks its 4 neighbors. If any are unvisited, it picks one
	randomly, removes the wall between them, moves there, and pushes the
	previous cell on a stack.
4. If all neighbors are visited, it backtracks by popping the stack.
5. When the stack is empty, every cell has been visited exactly once, yielding
	a perfect maze.

Solving the maze (BFS)
----------------------
1. Start at the visual top-left cell and target the visual bottom-right.
2. Use BFS to explore the maze level by level.
3. Track each cell's predecessor to rebuild the final path when the exit is
	reached.

Configuration
-------------
Edit these constants in maze.py to change the grid size and speed:
- ROWS, COLS
- GEN_DELAY, SOLVE_DELAY
